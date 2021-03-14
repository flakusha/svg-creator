import bpy, math, bmesh, random
from typing import Set

def rip_and_tear(context) -> Set:
    """Edge split geometry using specified angle or unique mesh settings.
    Also checks non-manifold geometry and hard edges.
    Returns set of colors that are used to color meshes."""
    processed = set()
    angle_use_fixed = context.preferences.addons["svg-creator"]\
        .preferences.RenderFixedAngleUse
    # Angle fixed in radians
    angle_fixed = context.preferences.addons["svg-creator"]\
        .preferences.RenderFixedAngle
    precision = context.preferences.addons["svg-creator"]\
        .preferences.RenderPrecision

    # Colors are saved in format specified by render precision parameter
    # Totally white and totally black colors are prohibited
    colors = set()
    # Apply split_n_paint function to every object and unite resulting colors
    colors.union(set([split_n_paint(context, colors, precision, obj,
    angle_use_fixed, angle_fixed, processed) for obj in context.scene.objects
    if obj.type == "MESH"]))

    return colors

def split_n_paint(context, colors, precision, obj, angle_use_fixed,
angle_fixed, processed):
    """Split edges of mesh and paint them with random color, add processed meshes into set to avoid splitting and painting them for the second time.
    Processed set is totally ignored in case scene has single-user objects and
    data, in this case everything will have unique and random colors, but 
    overall processing time will be increased."""

    if obj.data in processed:
        return
    else:
        processed.add(obj.data)
    
    if not angle_use_fixed:
        if obj.data.use_auto_smooth:
            angle_fixed = obj.data.auto_smooth_angle
        else:
            # If auto smooth is disabled, default edge split at 30 degrees can
            # lead to incorrect mesh appearance, nothing should be done
            # as it's 3D Artist decision to ignore this setting
            angle_fixed = math.pi

    # Add VCol layer to the model in case it already has one or has none
    if not "VCol" in obj.data.vertex_colors:
        vcol = bpy.ops.mesh.vertex_color_add()
        vcol.name = "VCol"
        vcol.active = True
        vcol.active_render = True
