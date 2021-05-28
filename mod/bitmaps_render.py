import bpy

def bitmaps_render(context: bpy.context):
    pref = context.preferences.addons["svg-creator"]\
        .preferences

    if pref.RenderAnimation:
        # anim_len = context.scene.frame_end - context.scene.frame_start
        anim_len = context.scene.frame_end - context.scene.frame_start
        for frame in range(anim_len + 1):
            bpy.context.scene.frame_set(frame)
            if pref.RenderVCol:
                
