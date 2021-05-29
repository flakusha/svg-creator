import bpy, math, bmesh, random
from typing import Set, Tuple

# Divisor coefficient for int colors
coef = {
    "8 bit":    255,
    "16 bit":   65535,
    "32 bit":   4294967295,
}
# Return this angle if it's not possible to calculate angle between faces
ang_limit = math.radians(89.0)
# Get preferences
prefs = bpy.context.preferences.addons["svg-creator"].preferences

def rip_and_tear(context) -> Set:
    """Edge split geometry using specified angle or unique mesh settings.

    Also checks non-manifold geometry and hard edges.

    Returns set of colors that are used to color meshes."""
    processed = set()
    angle_use_fixed = prefs.RenderFixedAngleUse
    # Angle fixed in radians
    angle_fixed = prefs.RenderFixedAngle
    precision = prefs.RenderPrecision

    # Colors are saved in format specified by render precision parameter
    # Totally white and totally black (and close to them) colors are prohibited
    colors = set()

    # Apply split_n_paint function to every object and unite resulting colors
    # colors.union(tuple(set(tuple([split_n_paint(context, colors, precision, obj,
    # angle_use_fixed, angle_fixed, processed) for obj in context.scene.objects
    # if obj.type == "MESH"]))))
    for obj in context.scene.objects:
        if obj.type == "MESH":
            if obj.data in processed or len(obj.data.polygons) == 0:
                processed.add(obj.data)
            else:
                colors.union(
                    split_n_paint(
                        context, colors, precision, obj,
                        angle_use_fixed, angle_fixed,
                        processed,
                    )
                )

    return colors

def split_n_paint(context, colors, precision, obj, angle_use_fixed,
angle_fixed, processed) -> Set[Tuple]:
    """Split edges of mesh and paint them with random color, add processed meshes into set to avoid splitting and painting them for the second time.

    Processed set is totally ignored in case scene has single-user objects and
    data, in this case every surface is guaranteed to have unique and random
    colors, but overall processing time will be increased."""

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
        # vcol = bpy.ops.mesh.vertex_color_add()
        vcol = obj.data.vertex_colors.new(name = "VCol", do_init = False)
        vcol.name = "VCol"
        vcol.active = True
        vcol.active_render = True

    bm = bmesh.new(use_operators = True)
    bm.from_mesh(obj.data)
    bm.select_mode = {"FACE"}
    # Generate indices in bmesh same as obj.data indices
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    for face in bm.faces:
        face.hide_set(False)
        face.select_set(False)

    # Split every mesh into chunks corresponding to smooth surfaces limited by
    # hard edges, basically it's bmesh implementation of edge split modifier.
    # Boundaries is the list for pairs of lists of vertices and edges for
    # bmesh.ops.split_edges operator
    boundaries = []
    for index, face in enumerate(bm.faces):
        # Select random face and grow selection till boundary is reached
        if not face.hide:
            bm.faces.active = bm.faces[index]
            # face_bm, active face
            fbm = bm.faces.active
            fbm.select_set(True)
            sel = False

            # List of selected faces
            sf = [fbm, ]

            # Grow selection until there is nothing new to select
            while not sel:
                # for selected current face in selected faces
                for fsc in sf:
                    # for edge in edges of selected faces
                    for e in fsc.edges:
                        # non-manifold geometry can lead to incorrect shading
                        # on surfaces where this kind of shading is not
                        # expected, so it's a good choice to split using
                        # non-manifold, edge smoothness is calculated when
                        # auto-smoothing tick is active
                        c0 = e.smooth
                        c1 = e.calc_face_angle(ang_limit) <= angle_fixed
                        c2 = e.is_manifold
                        c3 = not obj.data.edges[e.index].use_edge_sharp

                        if c0 and c1 and c2 and c3:
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
            boundaries.append((bv, be))

            # Hide and deselect processed mesh chunk,
            # so you can't access it again
            for f in sf:
                f.select_set(False)
                f.hide_set(True)

        # Unhide back, so operator can work with geometry
        for f in bm.faces:
            f.select_set(False)
            f.hide_set(False)
        
        # Finally split edges
        # Additional for loop because every change of bmesh demands indices
        # regeneration and c3 in edge check needs check in separate mesh
        # structure, because there is no access to edge mark data from bmesh
        for b in boundaries:
            bv, be = b[0], b[1]
            bmesh.ops.split_edges(bm, verts = bv, edges = be, use_verts = True)

    # Regenerate indices because bmesh have changed
    bm.faces.ensure_lookup_table()
    # Unhide and unselect faces to start painting
    for f in bm.faces:
        f.hide_set(False)
        f.select_set(False)

    # Paint every splitted chunk into random vertex color
    for index, face in enumerate(bm.faces):
        colors, _color, color_f = generate_color(context, colors, precision)

        # if not face.hide: # No need to check it anymore TODO remove
        bm.faces.active = bm.faces[index]
        fbm = bm.faces.active
        fbm.select_set(True)
        sel = False

        sf = [fbm, ]

        # Grow selection until there is nothing new to select
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

        vcol = bm.loops.layers.color.get("VCol")

        for f in sf:
            for loop in f.loops:
                loop[vcol] = (color_f[0], color_f[1], color_f[2], 1.0)

        for f in sf:
            f.select_set(False)
            f.hide_set(True)

    # Unhide faces, so there is no need to unhide faces after entering the
    # edit mode, speeds up work a bit
    for f in bm.faces:
        f.hide_set(False)

    # Remove doubles after coloring and edge split to avoid artifacts in
    # renders using any engine
    bmesh.ops.remove_doubles(bm, verts = [v for v in bm.verts], dist = 1e-5)
    bm.to_mesh(obj.data)
    obj.data.update()

    bm.free()

    return colors

def generate_color(context, colors, precision) -> (Set, Tuple, Tuple):
    """Generate random with desired precision and return it with updated
    color set. Colors are normalized in 0-1 range ever after, valid for VCol.

    8-bit have to be divided by 255,
    16-bit - by 65535,
    32-bit - by 4294967295."""

    # Black and dark colors are prohibited, because render doesn't store any
    # info in case there is no alpha is in picture.
    # About 0.4% precision step is cut from the bottom of the range
    # There is naive implementation of color regeneration re-checking new random
    # color is not in tuple, there should be way to do this better
    # TODO better random color creation algorithm
    if precision == "8 bit":
        color = tuple([random.randint(1, 255) for _ in range(3)])
        while color in colors:
            color = tuple([random.randint(1, 255) for _ in range(3)])
    elif precision == "16 bit":
        color = tuple([random.randint(250, 65_535) for _ in range(3)])
        while color in colors:
            color = tuple([random.randint(250, 65_535) for _ in range(3)])
    elif precision == "32 bit":
        color = tuple(
            [random.randint(1_750_000, 4_294_967_295) for _ in range(3)])
        while color in colors:
            color = tuple(
                [random.randint(1_750_000, 4_294_967_295) for _ in range(3)])

    colors.add(color)
    color_f = tuple([c / coef[precision] for c in color])
    return (colors, color, color_f)
