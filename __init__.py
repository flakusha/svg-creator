import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "mod"))

import bpy
from mathutils import Color
from bpy.types import PointerProperty
from bpy.utils import register_class, unregister_class
from . import preferences
from mod import svg_creation, ui

classes = (
    preferences.SVGC_Preferences,
    svg_creation.SVGC_OT_Main,
    ui.SVGC_PT_UI,
)

bl_info = {
    "name": "SVG Creator",
    "description": "Plugin creates SVG images from renders",
    "author": "flakusha",
    "version": (0, 0, 1),
    "blender": (2, 91, 0),
    "category": "Render",
    "location": "Properties > Output Properties",
    "tracker_url": "https://github.com/flakusha/svg-creator/issues",
}

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
