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
        revert_scene = context.preferences.addons["svg-creator"].\
            preferences.RevertScene
        render_discard = context.preferences.addons["svg-creator"].\
            preferences.RenderDiscard

        if revert_scene:
            bpy.ops.wm.revert_mainfile()
        elif render_discard:
            [setattr(context.scene.render, k, v) for k, v in
            render_settings_backup if not
            context.scene.render.is_property_readonly(k)]

def setup_render(context):
    """Function sets up the render to be compatible with tracing."""
    scene = context.scene
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
    scene.use_nodes = True

    # view layer settings
    view_layer = context.view_layer
    view_layer.use_pass_normal = True
    view_layer.use_pass_diffuse_color = True
    view_layer.use_pass_glossy_color = True
    view_layer.use_pass_emit = True

    if not "VColAOV" in view_layer.aovs:
        vcol_aov = bpy.ops.scene.view_layer_add_aov()
        vcol_aov.name = "VColAOV"
        vcol_aov.type = "COLOR"
