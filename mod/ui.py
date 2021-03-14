import bpy
from bpy.types import Panel

class SVGC_PT_UI(Panel):
    bl_label = "SVG Creator"
    bl_idname = "SVGC_PT_UI"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        svgcp = context.preferences.addons["svg-creator"].preferences
        row = layout.row()
        row.scale_y = 2.0
        row.operator("svg_creator.svg_create")

        layout.label(text = "Render settings:")
        col = layout.column()
        col.prop(svgcp, "SVGPath")
        row = layout.row(align = True)
        row.prop(svgcp, "RenderResolution")
        row = layout.row(align = True)
        row.prop(svgcp, "RenderFormat")
        row.prop(svgcp, "RenderPrecision")
        row = layout.row(align = True)
        row.prop(svgcp, "TracingThreadsNum")
        row.prop(svgcp, "TracingMemoryLimit")
        row = layout.row(align = True)
        row.prop(svgcp, "RenderAnimationMode")
        row = layout.row(align = True)
        row.prop(svgcp, "CameraMode")

        layout.label(text = "Scene processing options:")
        row = layout.row()
        row.prop(svgcp, "RenderOnly")
        row.prop(svgcp, "RevertScene")
        row.prop(svgcp, "RenderDiscard")

        layout.label(text = "Tracing settings:")
        row = layout.row()
        row.prop(svgcp, "RenderColorAnalysis")
        row = layout.row()
        row.prop(svgcp, "TracingEngine")
        col = layout.column(align = True)
        col.prop(svgcp, "TracingEnginePathPotrace")
        col.prop(svgcp, "TracingEnginePathImagetracer")
        col.prop(svgcp, "TracingEngineImagetracerNode")
        col.prop(svgcp, "TracingEnginePathRustrace")
        
        layout.label(text = "Geometry and image processing settings:")
        row = layout.row(align = True)
        row.prop(svgcp, "RenderFixedAngleUse")
        row.prop(svgcp, "RenderFixedAngle")

def register():
    bpy.utils.register_class(SVGC_PT_UI)

def unregister():
    bpy.utils.unregister_class(SVGC_PT_UI)
