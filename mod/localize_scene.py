import bpy

def localize_scene(context):
    """Pulls all the links into file, makes objects, data and materials local 
    to current file, optionally makes objects and object data single-user to
    randomize all tha paint."""
    single_user = context.preferences.addons["svg-creator"]\
        .preferences.RenderSingleUser

    for obj in bpy.context.scene.objects:
        obj.select_set(state = True)

    bpy.ops.object.make_local(type = "SELECT_OBDATA_MATERIAL")

    if single_user:
        bpy.ops.object.make_single_user(
            type = "SELECTED_OBJECTS", object = True, obdata = True)
