"""Scene-level properties."""

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty

try:
    from . import sites
except ImportError:
    import sites


def _site_items(self, context):
    items = []
    for s in sites.SITES:
        label = s["name"]
        if s.get("resale"):
            label += "  [OK to resell]"
        items.append((s["id"], label, s.get("license", "")))
    return items or [("polyhaven", "Poly Haven", "")]


def _category_items(self, context):
    try:
        try:
            from . import library
        except ImportError:
            import library
        cats = library.categories()
    except Exception:
        cats = []
    out = [("ALL", "All", "Show every texture")]
    for c in cats:
        out.append((c, c, ""))
    return out


def register():
    bpy.types.Scene.minitexture_query = StringProperty(
        name="Search",
        description="Search term, e.g. brick, wood, grass",
        default="",
    )
    bpy.types.Scene.minitexture_site = EnumProperty(
        name="Site",
        description="Texture source to open",
        items=_site_items,
    )
    bpy.types.Scene.minitexture_only_resale = BoolProperty(
        name="Only resale-safe",
        description="Show only CC0 / public-domain sources that permit resale",
        default=True,
    )
    bpy.types.Scene.minitexture_category = EnumProperty(
        name="Category",
        items=_category_items,
    )
    bpy.types.Scene.minitexture_import_path = StringProperty(
        name="Folder",
        description="Folder containing downloaded textures to import",
        default="",
        subtype="DIR_PATH",
    )
    bpy.types.Scene.minitexture_auto_apply = BoolProperty(
        name="Apply to selected object",
        description="Create a material and assign it to the active object",
        default=True,
    )


def unregister():
    for prop in (
        "minitexture_query",
        "minitexture_site",
        "minitexture_only_resale",
        "minitexture_category",
        "minitexture_import_path",
        "minitexture_auto_apply",
        "minitexture_enum",
    ):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
