import bpy

def setup_materials(context):
    """Modifies materials to include AOV outputs."""
    pass

def setup_compositor(context):
    """Sets up compositor for export."""

    aov_vcol = bpy.ops.node.add_node(type = "ShaderNodeOutputAOV")
    aov_vcol.name = "VertexColor"
