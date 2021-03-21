import bpy

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
    node_vcol = bpy.ops.node.add_node(type = "ShaderNodeVertexColor")
    node_vcol.layer_name = "VCol"
    node_vcol.location = (
        node_principled.location[0], node_principled.location[1] - 500)
    node_aov = bpy.ops.node.add_node(type = "ShaderNodeOutputAOV")
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
        add_rnd_node(context, "VCol", 200, True)

    if addon_preferences.RenderNormal:
        add_rnd_node(context, "Normal", 400)

    if addon_preferences.RenderDiffuse:
        add_rnd_node(context, "DiffCol", 600)

    # NOTE Specular in UI, Gloss in other parts of application
    if addon_preferences.RenderGlossy:
        add_rnd_node(context, "GlossCol", 800)

    if addon_preferences.RenderEmit:
        add_rnd_node(context, "Emit", 1000)

    context.area.ui_type = ui_type

def add_rnd_node(context, node_name: str, yloc = 0, is_aov = False):
    """Adds new nodes in compositor, picks info from Render Layer or AOV."""
    if is_aov:
        aov = bpy.ops.scene.view_layer_add_aov()
        aov.name = node_name

    node_save = bpy.ops.node.add_node(type = "CompositorNodeOutputFile")
    node_save.name = "{}Output".format(node_name)
    # NOTE Overwritten by SVGPath later
    node_save.base_path = "//"

    tree = context.scene.node_tree
    node_render = tree.nodes["Render Layers"]
    node_save.location =\
        (node_render.location[0] + 200, node_render.location[1] - yloc)

    links = tree.links
    _link = links.new(node_render.outputs[node_name], node_save.inputs[0])
