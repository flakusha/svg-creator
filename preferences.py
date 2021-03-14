import bpy, os, multiprocessing, math

from bpy.types import (
    Operator,
    Panel,
    PropertyGroup,
    AddonPreferences,
)

from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    CollectionProperty,
    StringProperty,
    PointerProperty,
    FloatVectorProperty,
)

imagetracerjs_path = os.path.join(os.path.dirname(__file__), "bin", 
    "imagetracerjs")
rustrace_path = os.path.join(os.path.dirname(__file__), "bin",
    "rustrace")

# Addon settings
class SVG_Creator_Properties(PropertyGroup):
    """Docstring"""

    # Render settings
    RenderResolution: FloatProperty(
        name = "Render resolution percentage",
        description = "Render size to be used in raster image creation",
        subtype = "PERCENTAGE",
        default = 100,
        min = 10, soft_max = 2000,
        step = 10, precision = 0,
    )
    RenderPrecision: EnumProperty(
        name = "Render precision",
        description = "Precision or renders, only use if 8 bit " +\
            "is not enough because there are a lot of surfaces' chunks",
        items = (
            ("8 bit", "8 bit", "8 bit images: BMP or PNG", ),
            ("16 bit", "16 bit", "16 bit images: PNG int or EXR float", ),
            ("32 bit", "32 bit", "32 bit images: EXR only", ),
        ),
        default = "8 bit",
    )
    RenderFormat: EnumProperty(
        name = "Render image format",
        description = "Image format which will be output for tracing",
        items = (
            ("BMP", "BMP", "Fastest for processing, but uncompressed", ),
            ("PNG", "PNG", "Slower processing, much smaller", ),
            ("EXR", "EXR", "Slower processing, smaller, high bit depth", ),
        ),
        default = "BMP",
    )
    RenderAnimation: BoolProperty(
        name = "Render Animation",
        description = "Render current frame, or render whole animation",
        default = False,
    )
    RenderAnimationMode: EnumProperty(
        name = "Animation Render Mode",
        description = "Render animation into separate or single SVGs",
        items = (
            ("Single", "Single SVG", "Render animation into single SVG",),
            ("Separate", "Separate SVGs", "Render frames into separate SVGs", ),
        ),
        default = "Single",
    )
    RenderFixedAngleUse: BoolProperty(
        name = "Use fixed angle",
        description = "Render all surfaces with split at angle",
        default = False,
    )
    RenderFixedAngle: FloatProperty(
        name = "Fixed angle",
        description = "Angle to use for geometry splitting",
        subtype = "ANGLE",
        default = math.radians(180),
        min = 0, max = 180,
    )

    # Camera settings
    CameraMode: EnumProperty(
        name = "Camera Mode",
        description = "Mode which is used to render scene to SVG",
        items = (
            ("Auto", "Auto mode", "Camera settings are used"),
            ("Perspective", "Perspective", "Camera will be set to perspective"),
            ("Ortho", "Orthographic", "Camera will be set to orthographic"),
            ("Panoramic", "Panoramic", "Camera will be set to panoramic"),
        ),
        default = "Auto",
    )

    # Scene render, revert or save
    RevertScene: BoolProperty(
        name = "Revert scene after processing",
        description = "Revert scene file after svg creation, WARNING: scene " +\
            "will be localized during processing, this is undone only with " +\
            "revert, although it's possible to save new file",
        default = True,
    )
    RenderDiscard: BoolProperty(
        name = "Discard render",
        description = "Discard new render settings after svg creation " +\
            "in case Cycles render was used originally",
        default = True,
    )
    RenderOnly: BoolProperty(
        name = "Only render images",
        description = "Render only images, don't trace SVGs",
        default = False,
    )
    RenderSave: BoolProperty(
        name = "Save into separate file",
        description = "Save render into separate file",
        default = False,
    )
    RenderColorAnalysis: EnumProperty(
        name = "Render color analysis mode",
        description = "After render colors in image",
        items = (
            ("Native", "Python color search",
            "Python image color analysis, slow, but doesn't need additional " +\
            "compilation and setup", ),
            ("Rust", "Rust color search",
            "Rust image color analysis, fast, but needs additional binary " +\
            "library compilation for Python",
            ),
        ),
        default = "Native",
    )

    # Tracing engines settings
    TracingEngine: EnumProperty(
        name = "Tracing engine",
        description = "Engine to use for SVG creation",
        items = (
            ("Potrace", "Potrace engine",
            "Potrace engine by Peter Selinger", ),
            ("Rustrace", "Rustrace", "Rustrace engine by addon's author", ),
            ("ImageTracerJS", "ImageTracerJS",
            "ImageTracerJS by András Jankovics", ),
        ),
        default = "Potrace",
    )
    TracingEnginePathPotrace: StringProperty(
        name = "Potrace Path",
        description = "Path for Potrace engine",
        default = "potrace",
        subtype = "FILE_PATH",
    )
    TracingEnginePathImagetracer: StringProperty(
        name = "ImagetracerJS Path",
        description = "Path for ImagetracerJS engine",
        default = "",
        subtype = "FILE_PATH",
    )
    TracingEnginePathRustrace: StringProperty(
        name = "Rustrace Path",
        description = "Path for Rustrace engine",
        default = rustrace_path,
        subtype = "DIR_PATH",
    )
    ImagemagickPath: StringProperty(
        name = "ImageMagick Path",
        description = "ImageMagick binaries folder path",

    )
    TracingThreadsNum: IntProperty(
        name = "Number of threads",
        description = "Number of threads to use during tracing",
        default = multiprocessing.cpu_count(),
        min = 1, soft_max = 256,
    )
    TracingMemoryLimit: IntProperty(
        name = "Amount of RAM (MB)",
        description = "Amount of RAM used for tracing (only for compatible " +\
        "algorithms",
        default = 1024,
    )

    RemoveImages: BoolProperty(
        name = "Remove renders after processing",
        description = "Remove rendered raster images after SVG creation",
        default = True,
    )
    RemoveMasks: BoolProperty(
        name = "Remove masks",
        description = "Remove masks used for tracing",
        default = True,
    )


class SVG_Creator_Preferences(AddonPreferences):
    bl_idname = __package__
    print("Debug: bl_idname:", __package__)

def register():
    bpy.utils.register_class(SVG_Creator_Properties)
    bpy.utils.register_class(SVG_Creator_Preferences)

def unregister():
    bpy.utils.unregister_class(SVG_Creator_Preferences)
    bpy.utils.unregister_class(SVG_Creator_Properties)
