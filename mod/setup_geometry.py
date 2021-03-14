import bpy, math, bmesh, random
from typing import Set, Tuple

coef = {
    "8 bit": 255,
    "16 bit": 65535,
    "32 bit": 4294967295,
}

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
    colors.union(set(tuple([split_n_paint(context, colors, precision, obj,
    angle_use_fixed, angle_fixed, processed) for obj in context.scene.objects
    if obj.type == "MESH"])))

    colors.remove(None)
    return colors

def split_n_paint(context, colors, precision, obj, angle_use_fixed,
angle_fixed, processed):
    """Split edges of mesh and paint them with random color, add processed meshes into set to avoid splitting and painting them for the second time.
    Processed set is totally ignored in case scene has single-user objects and
    data, in this case everything will have unique and random colors, but
    overall processing time will be increased."""

    if obj.data in processed or len(obj.data.polygons) < 1:
        return None
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

    bm = bmesh.new(use_operators = True)
    bm.from_mesh(obj.data)
    bm.select_mode = {"FACE"}
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    for face in bm.faces:
        face.hide_set(False)
        face.select_set(False)

    for index, face in enumerate(bm.faces):
        # Select random face and grow selection till hard boundary is reached
        if not face.hide:
            bm.faces.active = bm.faces[index]
            # face_bm, active face
            fbm = bm.faces.active
            fbm.select_set(True)
            sel = False

            # List of selected faces
            sf = [fbm, ]

            while not sel:
                # for selected current face in selected faces
                for fsc in sf:
                    # for edge in edges of selected faces
                    for e in fsc.edges:
                        c0 = e.smooth
                        c1 = e.calc_face_angle(math.radians(89.9))\
                        <= angle_fixed
                        # non-manifold geometry can lead to weird shading
                        # c2 = not e.is_manifold
                        if c0 and c1:
                            # Select linked faces
                            [lf.select_set(True) for lf in e.link_faces]

                # Temp tuple of selected geometry
                sft = [f for f in bm.faces if f.select]

                # Selection is exausted
                if sft == sf:
                    sel = True
                else:
                    sf = sft

            # Tuples of selected vertices and edges
            sv = tuple([v for v in bm.verts if v.select])
            se = tuple([e for e in bm.edges if e.select])

            # Sets of boundary vertices and edges
            bv = set()
            be = set()

            # Get boundary vertices and edges
            for v in sv:
                for le in v.link_edges:
                    if not le.select:
                        bv.add(v)
            for e in se:
                for lf in e.link_faces:
                    if not lf.select:
                        be.add(e)

            bv = list(bv)
            be = list(be)

            bmesh.ops.split_edges(bm, verts = bv, edges = be, use_verts = True)

            # Hide and deselect processed mesh chunk,
            # so you can't access it again
            for f in sf:
                f.select_set(False)
                f.hide_set(True)

    # Unhide and unselect faces to start painting
    bm.faces.ensure_lookup_table()

    for f in bm.faces:
        f.hide_set(False)
        f.select_set(False)

    for index, face in enumerate(bm.faces):
        colors, _color, color_f = generate_color(context, colors)

        if not face.hide:
            bm.faces.active = bm.faces[index]
            fbm = bm.faces.active
            fbm.select_set(True)
            sel = False

            sf = [fbm, ]

            while not sel:
                se = tuple([e for e in bm.edges if e.select])
                for e in se:
                    for f in e.link_faces:
                        f.select_set(True)

                sft = [f for f in bm.faces if f.select]

                if sf == sft:
                    sel = True
                else:
                    sf = sft

            vcol = bm.loops.color.get("VCol")

            for f in sf:
                for loop in f.loops:
                    loop[vcol] = (color_f[0], color_f[1], color_f[2])

            for f in sf:
                f.select_set(False)
                f.hide_set(True)

    for f in bm.faces:
        f.hide_set(False)

    bm.to_mesh(obj.data)
    obj.data.update()

    bm.free()

    return colors

def generate_color(context, colors) -> (Set, Tuple, Tuple):
    """Generate random with desired precision and return it with updated
    color set. Colors are normalized in 0-1 range, valid for VCol.
    8-bit have to be divided by 255, 16-bit - by 65535,
    32-bit - by 4294967295."""

    # Black and White colors are prohibited
    # 0 and 255 are excluded for 8-bit
    # 0-1000 and 65435-65535 are excluded for 16-bit
    # 0-10000000 and 4284967295-4294967295 are excluded for 32-bit
    render_precision = context.preferences.addons["svg-creator"]\
        .preferences.RenderPrecision

    if render_precision == "8 bit":
        color = tuple([random.randint(1, 254) for _ in range(3)])
        while color in colors:
            color = tuple([random.randint(1, 254) for _ in range(3)])
    elif render_precision == "16 bit":
        color = tuple([random.randint(100, 65425) for _ in range(3)])
        while color in colors:
            color = tuple([random.randint(100, 65425) for _ in range(3)])
    elif render_precision == "32 bit":
        color = tuple(
            [random.randint(10_000_000, 4284967295) for _ in range(3)])
        while color in colors:
            color = tuple(
                [random.randint(10_000_000, 4284967295) for _ in range(3)])

    colors.add(color)
    color_f = tuple([c / coef[render_precision] for c in color])
    return (colors, color, color_f)