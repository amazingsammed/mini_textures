bl_info = {
    "name": "Mini Texture",
    "author": "Mini Texture",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "View3D > Sidebar > Mini Texture",
    "description": "Browse CC0 texture sites, download CC0 textures, and apply or generate materials",
    "category": "Add Material",
}

import importlib

import bpy

from . import downloads, library, operators, preferences, properties, sites, ui

_modules = (sites, library, properties, preferences, downloads, operators, ui)


def _reload():
    for mod in _modules:
        try:
            importlib.reload(mod)
        except Exception:
            pass


def register():
    preferences.register()
    properties.register()
    downloads.register()
    operators.register()
    ui.register()
    try:
        library.refresh()
    except Exception as exc:  # library scan must never block loading
        print("[Mini Texture] library scan failed:", exc)


def unregister():
    ui.unregister()
    operators.unregister()
    downloads.unregister()
    properties.unregister()
    preferences.unregister()
    library.clear_previews()


if __name__ == "__main__":
    _reload()
    register()
