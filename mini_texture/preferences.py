"""Add-on preferences."""

import os

import bpy
from bpy.props import StringProperty


class MiniTexturePreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    library_path: StringProperty(
        name="My Library Folder",
        description="Folder scanned for textures you import or download",
        default="",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "library_path")
        box = layout.box()
        box.label(text="Tip: download from a CC0 source, then use", icon="INFO")
        box.label(text="'Import Folder' to add the files to your library.")


def register():
    bpy.utils.register_class(MiniTexturePreferences)


def unregister():
    bpy.utils.unregister_class(MiniTexturePreferences)
