import bpy, time
from bpy.types import Operator
from . check_settings import check_settings
from . localize_scene import localize_scene
from . setup_geometry import rip_and_tear
from . setup_visuals import setup_materials, setup_compositor
from . setup_render import save_render_settings, setup_render
from . bitmaps_render import bitmaps_render
from . bitmaps_trace import bitmaps_trace

class SVGC_OT_Main(Operator):
    """Creates SVG using given parameters. Works in object mode."""
    bl_idname = "svg_creator.svg_create"
    bl_label = "Create SVG"
    # No "UNDO" in bl_options, so undo is not possible
    bl_options = {"REGISTER", }

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        time_creation = time.time()
        create_svg(context)
        time_creation_finish = (time.time() - time_creation) / 60
        print("Info: SVG render took {:.3f} minutes"\
            .format(time_creation_finish))
        return {"FINISHED"}

def create_svg(context):
    """Checks if it's possible to run operator, backups render settings,
    sets up render, localizes scene, colors every mesh in the scene, sets up
    materials, sets up compositor, renders bitmaps and then traces them into
    SVGs."""
    # Abort execution if settings are conflicting
    check_settings(context)

    render_settings_backup = save_render_settings(context, "SAVE")
    setup_render(context)

    localize_scene(context)

    rip_and_tear(context)
    setup_materials(context)
    setup_compositor(context)

    bitmaps = bitmaps_render(context)
    bitmaps_trace(context, bitmaps)

    save_render_settings(context, "RESTORE", render_settings_backup)

def register():
    bpy.utils.register_class(SVGC_OT_Main)

def unregister():
    bpy.utils.unregister_class(SVGC_OT_Main)