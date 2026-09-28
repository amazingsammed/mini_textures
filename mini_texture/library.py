"""Local texture library: scans bundled + user folders and caches previews."""

import os

import bpy
from bpy.utils import previews as _previews_module

try:
    from . import sites  # noqa: F401
except Exception:
    pass

KIND_SUFFIXES = {
    "diffuse": "diffuse",
    "diff": "diffuse",
    "albedo": "diffuse",
    "col": "diffuse",
    "color": "diffuse",
    "basecolor": "diffuse",
    "normal": "normal",
    "nrm": "normal",
    "nor": "normal",
    "normalgl": "normal",
    "normaldx": "normal",
    "roughness": "roughness",
    "rough": "roughness",
    "rgh": "roughness",
    "height": "displacement",
    "disp": "displacement",
    "displacement": "displacement",
    "ao": "ao",
    "ambientocclusion": "ao",
    "occlusion": "ao",
    "metallic": "metallic",
    "metalness": "metallic",
    "specular": "specular",
    "opacity": "opacity",
    "alpha": "opacity",
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".exr"}

_PREVIEWS = None
_ITEMS = []          # list of dicts: name, category, tags, files{kind:path}, icon
_BY_NAME = {}


def _previews():
    global _PREVIEWS
    if _PREVIEWS is None:
        _PREVIEWS = _previews_module.new()
    return _PREVIEWS


def bundled_dir():
    return os.path.join(os.path.dirname(__file__), "textures")


def thumbs_dir():
    return os.path.join(os.path.dirname(__file__), "thumbs")


def user_dir():
    try:
        prefs = bpy.context.preferences.addons[__package__].preferences
        path = bpy.path.abspath(prefs.library_path)
        if path:
            os.makedirs(path, exist_ok=True)
            return path
    except Exception:
        pass
    fallback = os.path.join(
        bpy.utils.user_resource("DATAFILES", path="mini_texture", create=True)
    )
    os.makedirs(fallback, exist_ok=True)
    return fallback


def _split_kind(stem):
    low = stem.lower()
    for suffix, kind in KIND_SUFFIXES.items():
        if low.endswith("_" + suffix):
            return stem[: -(len(suffix) + 1)], kind
        if low.endswith("-" + suffix):
            return stem[: -(len(suffix) + 1)], kind
    return stem, "diffuse"


def _scan_folder(folder, category, items, tags):
    if not folder or not os.path.isdir(folder):
        return
    for entry in sorted(os.listdir(folder)):
        full = os.path.join(folder, entry)
        if os.path.isdir(full):
            # one level of sub-folders becomes its category
            _scan_folder(full, entry, items, tags)
            continue
        stem, ext = os.path.splitext(entry)
        if ext.lower() not in IMAGE_EXTS:
            continue
        base, kind = _split_kind(stem)
        item = items.setdefault(
            base,
            {"name": base, "category": category, "tags": tags, "files": {}},
        )
        item["files"][kind] = full


def _make_icon(name, item):
    previews = _previews()
    key = "mintx_" + name
    if key in previews:
        return previews[key].icon_id
    thumb = os.path.join(thumbs_dir(), name + ".png")
    src = thumb if os.path.isfile(thumb) else item["files"].get("diffuse")
    if not src or not os.path.isfile(src):
        return 0
    try:
        return previews.load(key, src, "IMAGE").icon_id
    except Exception:
        return 0


def build(force=False):
    """(Re)scan all library folders and refresh previews."""
    global _ITEMS, _BY_NAME
    if _ITEMS and not force:
        return _ITEMS

    items = {}
    _scan_folder(bundled_dir(), "Bundled (CC0)", items, "free,cc0")
    _scan_folder(user_dir(), "My Library", items, "imported")

    _ITEMS = []
    _BY_NAME = {}
    for name, item in sorted(items.items(), key=lambda kv: kv[0].lower()):
        item["icon"] = _make_icon(name, item)
        item["has_normal"] = "normal" in item["files"]
        item["has_roughness"] = "roughness" in item["files"]
        _ITEMS.append(item)
        _BY_NAME[name] = item

    # keep enum values in sync
    try:
        _sync_enum()
    except Exception:
        pass
    return _ITEMS


def _sync_enum():
    values = [(it["name"], it["name"], it["category"]) for it in _ITEMS]
    if not values:
        values = [("NONE", "None", "No textures found")]
    bpy.types.Scene.minitexture_enum = bpy.props.EnumProperty(
        name="Texture", items=values
    )


def refresh():
    return build(force=True)


def get(name):
    if not _ITEMS:
        build()
    return _BY_NAME.get(name)


def all_items():
    if not _ITEMS:
        build()
    return _ITEMS


def categories():
    cats = []
    for it in all_items():
        if it["category"] not in cats:
            cats.append(it["category"])
    return cats


def user_library_files():
    """Flat list of image files in the user library (for the import list)."""
    out = []
    folder = user_dir()
    for root, _dirs, files in os.walk(folder):
        for f in files:
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                out.append(os.path.join(root, f))
    return sorted(out)


def clear_previews():
    global _PREVIEWS, _ITEMS, _BY_NAME
    if _PREVIEWS is not None:
        try:
            _PREVIEWS.clear()
            _previews_module.remove(_PREVIEWS)
        except Exception:
            pass
        _PREVIEWS = None
    _ITEMS = []
    _BY_NAME = {}
