import bpy

def save_render_settings(context, mode: str, render_settings_backup = None):
    """Function saves and restores render settings."""
    if mode.upper() == "SAVE":
        if context.scene.render.engine == "BLENDER_EEVEE":
            render_settings_backup = [
                (key, getattr(context.scene.render, key))
                for key in dir(context.scene.render)
                if not key.startswith("__")
            ]
            return render_settings_backup
        else:
            context.scene.render.engine = "BLENDER_EEVEE"
            return None

    elif mode.upper() == "RESTORE" and render_settings_backup:
        prefs = context.preferences.addons["svg-creator"].preferences
        revert_scene = prefs.RevertScene
        render_discard = prefs.RenderDiscard

        return

        # TODO Disabled for now, must be added after stable version is available
        if revert_scene:
            bpy.ops.wm.revert_mainfile()
        elif render_discard:
            [setattr(context.scene.render, k, v) for k, v in
            render_settings_backup if not
            context.scene.render.is_property_readonly(k)]

def setup_render(context):
    """Function sets up the render to be compatible with tracing."""
    scene = context.scene
    addon_preferences = context.preferences.addons["svg-creator"].preferences
    render_format = addon_preferences.RenderFormat
    render_precision = addon_preferences.RenderPrecision.split(" ")[0]

    # eevee render settings
    # NOTE As buffers are used, there is no need in samples > 1
    scene.eevee.taa_render_samples = 1
    scene.eevee.use_gtao = False
    scene.eevee.use_bloom = False
    scene.eevee.use_ssr = False
    scene.eevee.use_motion_blur = False
    scene.eevee.use_volumetric_lights = False
    scene.render.use_high_quality_normals = True
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = render_format
    # NOTE Correct depth must be controlled using check_settings()
    if render_format in ("PNG", "OPEN_EXR"):
        scene.render.image_settings.color_depth = render_precision

    scene.use_nodes = True

    # view layer settings
    view_layer = context.view_layer
    view_layer.use_pass_normal = True
    view_layer.use_pass_diffuse_color = True
    view_layer.use_pass_glossy_color = True
    view_layer.use_pass_emit = True

    if not "VCol" in view_layer.aovs:
        aov = view_layer.aovs.add()
        aov.name = "VCol"
        aov.type = "COLOR"

    # NOTE Shouldn't work in --background mode, so try except
    try:
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        if space.type == "SpaceView3D":
                            if space.shading.type == "SOLID":
                                space.shading.color_type = "VERTEX"
                                # I enjoy typing
    except:
        pass
