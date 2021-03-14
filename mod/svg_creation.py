import bpy, time
from bpy.types import Operator

class SVGC_OT_Main(Operator):
    """Creates SVG using given parameters"""
    bl_idname = "svg_creator.svg_create"
    bl_label = "Create SVG"
    bl_options = {"REGISTER", }

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        time_creation = time.time()
        create_svg()
        time_creation_finish = (time.time() - time_creation) / 60
        print("Info: SVG render took {:.3f} minutes"\
            .format(time_creation_finish))
        return {"FINISHED"}

def create_svg():
    context = bpy.context
    if context.scene.render.engine == "CYCLES":
        render_settings_backup = [
            (key, getattr(context.scene.render, key))
            for key in dir(context.scene.render)
            if not key.startswith("__")
        ]
    else:
        bpy.context.scene.render.engine = "CYCLES"

    localize_scene()
    setup_render(context)
    setup_compositor()
    rip_and_tear()
    render_bitmaps()

    if context.scene.SVG_Creator.RevertScene:
        bpy.ops.wm.revert_mainfile()
    elif not context.scene.SVG_Creator.RevertScene and\
    context.scene.SVG_Creator.RenderDiscard:
        [setattr(context.scene.render, k, v) for k, v in render_settings_backup
        if not context.scene.render.is_property_readonly(k)]
    elif context.scene.SVG_Creator.RenderDiscard:
        [setattr(context.scene.render, k, v) for k, v in render_settings_backup
        if not context.scene.render.is_property_readonly(k)]

def register():
    bpy.utils.register_class(SVGC_OT_Main)

def unregister():
    bpy.utils.unregister_class(SVGC_OT_Main)