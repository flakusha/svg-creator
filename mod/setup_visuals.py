import os, bpy

def setup_materials(context):
    """Modifies materials to include AOV outputs."""
    ui_type = context.area.ui_type
    context.area.ui_type = "ShaderNodeTree"

    # Don't modify already processed materials
    processed = set()
    for obj in context.scene.objects:
        if obj.type == "MESH":
            if obj.data.materials:
                for i, mat in enumerate(obj.data.materials):
                    if mat not in processed:
                        setup_material(context, obj, i, mat)
                        processed.add(mat)
            else:
                # May not be unique "SVGC Material.xxx", managed by Blender
                mat = obj.data.materials.new("SVGC Material")
                setup_material(context, obj, i, mat)
                processed.add(mat)

    context.area.ui_type = ui_type

def setup_material(context, obj, i: int, mat):
    """Adds VCol AOV to current node setup. Other nodes are not modified."""
    obj.active_material_index = i
    mat.use_nodes = True
    tree = mat.node_tree
    node_principled = tree.nodes["Principled BSDF"]
    node_vcol = tree.nodes.new("ShaderNodeVertexColor")
    node_vcol.layer_name = "VCol"
    node_vcol.location = (
        node_principled.location[0], node_principled.location[1] - 800)
    node_aov = tree.nodes.new("ShaderNodeOutputAOV")
    node_aov.name = "VCol"
    node_aov.location = (node_vcol.location[0] + 200, node_vcol.location[1])

    links = tree.links
    _link = links.new(node_vcol.outputs["Color"], node_aov.inputs["Color"])

def setup_compositor(context):
    """Sets up compositor for export using render and AOV."""
    ui_type = context.area.ui_type
    context.area.ui_type = "CompositorNodeTree"
    context.scene.use_nodes = True

    addon_preferences = context.preferences.addons["svg-creator"].preferences

    if addon_preferences.RenderVCol:
        # NOTE AOV output for Render Layer is added during setup_render()
        add_rnd_node(context, "VCol", 300)

    if addon_preferences.RenderNormal:
        add_rnd_node(context, "Normal", 450)

    if addon_preferences.RenderDiffuse:
        add_rnd_node(context, "DiffCol", 600)

    # NOTE Specular in UI, Gloss in other parts of application
    if addon_preferences.RenderGlossy:
        add_rnd_node(context, "GlossCol", 750)

    if addon_preferences.RenderEmit:
        add_rnd_node(context, "Emit", 900)

    context.area.ui_type = ui_type

def add_rnd_node(context, node_name: str, yloc = 0):
    """Adds new nodes in compositor, picks info from Render Layer or AOV."""
    addon_preferences = context.preferences.addons["svg-creator"].preferences
    tree = context.scene.node_tree

    node_save = tree.nodes.new("CompositorNodeOutputFile")
    # node_save = bpy.ops.node.add_node(type = "CompositorNodeOutputFile")
    node_save.name = "{}Output".format(node_name)
    node_save.base_path = addon_preferences.SVGPath

    node_render = tree.nodes["Render Layers"]
    node_save.location =\
        (node_render.location[0] + 300, node_render.location[1] - yloc)

    links = tree.links
    _link = links.new(node_render.outputs[node_name], node_save.inputs[0])

    # Name output file for every node
    node_save.file_slots[0].path = "{}_{}_######".format(
        os.path.basename(bpy.data.filepath), node_name)

    # NOTE OpenEXR provides several methods of compression:
    # RLE is good for ID maps and other solid colors -> pick it for VCol, Emit
    # ZIP is good for texture maps -> pick it for Diffuse, Specular and Normal
    # PIZ is good for grainy images -> don't use it
    # NOTE PNG provides good compression, to get optimal balance between
    # preformance and file size this script sets PNG compression to 75%
    # ID/VCol/Emit bitmaps will benefit from this setting

    if addon_preferences.RenderFormat == "BMP":
        node_save.file_slots[0].save_as_render = False

    elif addon_preferences.RenderFormat == "PNG":
        node_save.file_slots[0].use_node_format = False
        node_save.file_slots[0].save_as_render = False
        node_save.file_slots[0].format.file_format =\
            addon_preferences.RenderFormat
        node_save.file_slots[0].format.color_depth =\
            addon_preferences.RenderPrecision.split(" ")[0]
        node_save.file_slots[0].format.color_mode = "RGB"
        node_save.file_slots[0].format.compression = 75

    elif addon_preferences.RenderFormat == "OPEN_EXR":
        node_save.file_slots[0].use_node_format = False
        node_save.file_slots[0].format.file_format =\
            addon_preferences.RenderFormat
        node_save.file_slots[0].format.color_depth =\
            addon_preferences.RenderPrecision.split(" ")[0]
        node_save.file_slots[0].format.color_mode = "RGB"

        if node_name in ("VCol", "Emit"):
            node_save.file_slots[0].format.exr_codec = "RLE"
        elif node_name in ("DiffCol", "GlossCol", "Normal"):
            node_save.file_slots[0].format.exr_codec = "ZIP"
