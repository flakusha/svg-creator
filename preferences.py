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

class SVGC_Preferences(AddonPreferences):
    bl_idname = __package__

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
        description = "Image format for tracing",
        items = (
            ("BMP", "BMP", "Fastest for processing, but uncompressed, 8 bit", ),
            ("PNG", "PNG", "Slower processing, much smaller, 8+ bit", ),
            ("OPEN_EXR", "EXR", "Slower processing, smaller, 16+ bit", ),
        ),
        default = "BMP",
    )
    RenderColorAnalysis: EnumProperty(
        name = "Render Color Analyzer",
        description = "Algorithm for render colors analysis",
        items = (
            ("Python", "Native Python", "Slow mode, no libraries required", ),
            ("Rust", "Rust Color Detector", "Fast, needs to be compiled", ),
        ),
        default = "Python",
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

    # Render different buffers to get more lines traced in final image
    RenderVCol: BoolProperty(
        name = "Render Vertex Colors",
        description = "Render Vertex Colors painted during geometry setup",
        default = True,
    )
    RenderNormal: BoolProperty(
        name = "Render Normal",
        description = "Use Normal buffer in render",
        default = True,
    )
    RenderDiffuse: BoolProperty(
        name = "Render Diffuse",
        description = "Use Diffuse buffer in render",
        default = True,
    )
    # NOTE Specular in UI, Gloss in other parts of application
    RenderGlossy: BoolProperty(
        name = "Render Specular",
        description = "Use Specular(Glossy) buffer in render",
        default = True,
    )
    RenderEmit: BoolProperty(
        name = "Render Emission",
        description = "Use Emission buffer in render",
        default = True,
    )

    # Camera settings
    CameraMode: EnumProperty(
        name = "Camera Mode",
        description = "Mode which is used to render scene to SVG",
        items = (
            ("Auto", "Auto", "Current Camera settings are used"),
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
            "in case Eevee render was used originally",
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
    RenderSingleUser: BoolProperty(
        name = "Single User Data",
        description = "Make all object data single user, every object will " +\
            "have unque set of colors",
        default = False,
    )

    # Tracing engines settings
    TracingEngine: EnumProperty(
        name = "Tracing engine",
        description = "Engine to use for SVG creation",
        items = (
            ("Potrace", "Potrace engine",
            "Potrace engine by Peter Selinger", ),
            ("ImageTracerJS", "ImageTracerJS",
            "ImageTracerJS by András Jankovics", ),
            ("Rustrace", "Rustrace", "Rustrace engine by addon's author", ),
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
        default = imagetracerjs_path,
        subtype = "FILE_PATH",
    )
    TracingEngineImagetracerNode: StringProperty(
        name = "Node.js Path",
        description = "Node.js is needed to run ImagetracerJS",
        default = "node",
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

    # Output settings
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
    SVGPath: StringProperty(
        name = "SVG Output Destination",
        description = "Folder for SVGs",
        default = "//",
        subtype = "DIR_PATH",
    )



def register():
    bpy.utils.register_class(SVGC_Preferences)

def unregister():
    bpy.utils.unregister_class(SVGC_Preferences)
