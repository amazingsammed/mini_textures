"""In-addon search + download for ambientCG (CC0)."""

import json
import os
import tempfile
import urllib.parse
import urllib.request
import zipfile

import bpy
from bpy.props import CollectionProperty, EnumProperty, IntProperty, StringProperty
from bpy.types import Operator, PropertyGroup

try:
    from . import library
except ImportError:
    import library


API = "https://ambientcg.com/api/v2/full_json"
GET = "https://ambientcg.com/get?file="
USER_AGENT = "MiniTextureBlenderAddon/1.0"

# mapping of ambientCG file-name tokens -> our library "kind" suffixes
MAP_TOKENS = [
    ("color", "diffuse"),
    ("normalgl", "normal"),
    ("normaldx", "normal"),
    ("normal", "normal"),
    ("roughness", "roughness"),
    ("metalness", "metallic"),
    ("metallic", "metallic"),
    ("ambientocclusion", "ao"),
    ("displacement", "displacement"),
    ("emission", "emissive"),
    ("opacity", "opacity"),
    ("alpha", "opacity"),
]


class AmbientCGResult(PropertyGroup):
    asset_id: StringProperty()
    name: StringProperty()
    preview: StringProperty()
    page: StringProperty()


def _get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download(url, dest, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as fh:
        while True:
            chunk = resp.read(262144)
            if not chunk:
                break
            fh.write(chunk)


def _rename_maps(folder, asset_id):
    """Give extracted files clean '<asset>_<kind>.<ext>' names."""
    renamed = 0
    for root, _dirs, files in os.walk(folder):
        for f in files:
            stem, ext = os.path.splitext(f)
            low = stem.lower()
            kind = None
            for token, k in MAP_TOKENS:
                if low.endswith(token):
                    kind = k
                    break
            if not kind:
                continue
            target = os.path.join(root, "%s_%s%s" % (asset_id, kind, ext.lower()))
            src = os.path.join(root, f)
            if os.path.abspath(src) != os.path.abspath(target):
                try:
                    if os.path.exists(target):
                        os.remove(target)
                    os.rename(src, target)
                    renamed += 1
                except OSError:
                    pass
    return renamed


class MINTEXTURE_OT_acg_search(Operator):
    bl_idname = "minitexture.acg_search"
    bl_label = "Search ambientCG"
    bl_description = "Search ambientCG (CC0) and list the results below"

    def execute(self, context):
        query = context.scene.minitexture_query.strip()
        params = {
            "type": "Material",
            "limit": "24",
            "include": "downloadable",
            "sort": "popular",
        }
        if query:
            params["q"] = query
        url = API + "?" + urllib.parse.urlencode(params)
        try:
            data = _get_json(url)
        except Exception as exc:
            self.report({"ERROR"}, "Network error: %s" % exc)
            return {"CANCELLED"}

        results = data.get("foundAssets", [])
        coll = context.scene.minitexture_acg_results
        coll.clear()
        for asset in results:
            asset_id = asset.get("assetId", "")
            if not asset_id:
                continue
            item = coll.add()
            item.asset_id = asset_id
            item.name = asset.get("displayName") or asset_id
            previews = asset.get("previewImage") or {}
            item.preview = previews.get("256-PNG") or previews.get("256-JPG-FFFFFF", "")
            item.page = asset.get("shortLink") or ("https://ambientcg.com/a/" + asset_id)
        self.report({"INFO"}, "Found %d results" % len(coll))
        return {"FINISHED"}


class MINTEXTURE_OT_acg_download(Operator):
    bl_idname = "minitexture.acg_download"
    bl_label = "Download"
    bl_description = "Download the highlighted asset into My Library"
    bl_options = {"REGISTER", "UNDO"}

    resolution: EnumProperty(
        name="Resolution",
        items=[("1K", "1K", ""), ("2K", "2K", ""), ("4K", "4K", "")],
        default="1K",
    )
    fmt: EnumProperty(
        name="Format",
        items=[("JPG", "JPG", ""), ("PNG", "PNG", "")],
        default="JPG",
    )

    def execute(self, context):
        scene = context.scene
        coll = scene.minitexture_acg_results
        if not coll:
            self.report({"ERROR"}, "Run a search first")
            return {"CANCELLED"}
        idx = max(0, min(scene.minitexture_acg_index, len(coll) - 1))
        asset_id = coll[idx].asset_id

        filename = "%s_%s-%s.zip" % (asset_id, self.resolution, self.fmt)
        url = GET + urllib.parse.quote(filename)

        dest_dir = os.path.join(library.user_dir(), asset_id)
        os.makedirs(dest_dir, exist_ok=True)

        tmp_zip = os.path.join(tempfile.gettempdir(), filename)
        try:
            _download(url, tmp_zip)
        except Exception as exc:
            self.report({"ERROR"}, "Download failed: %s" % exc)
            return {"CANCELLED"}

        try:
            with zipfile.ZipFile(tmp_zip) as zf:
                zf.extractall(dest_dir)
        except Exception as exc:
            self.report({"ERROR"}, "Unzip failed: %s" % exc)
            return {"CANCELLED"}
        finally:
            try:
                os.remove(tmp_zip)
            except OSError:
                pass

        _rename_maps(dest_dir, asset_id)
        library.refresh()
        self.report({"INFO"}, "Downloaded %s" % asset_id)
        return {"FINISHED"}


class MINTEXTURE_OT_acg_open_page(Operator):
    bl_idname = "minitexture.acg_open_page"
    bl_label = "Open Page"

    def execute(self, context):
        scene = context.scene
        coll = scene.minitexture_acg_results
        if not coll:
            return {"CANCELLED"}
        idx = max(0, min(scene.minitexture_acg_index, len(coll) - 1))
        page = coll[idx].page
        if page:
            try:
                bpy.ops.wm.url_open(url=page)
            except Exception:
                pass
        return {"FINISHED"}


CLASSES = (
    AmbientCGResult,
    MINTEXTURE_OT_acg_search,
    MINTEXTURE_OT_acg_download,
    MINTEXTURE_OT_acg_open_page,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.minitexture_acg_results = CollectionProperty(type=AmbientCGResult)
    bpy.types.Scene.minitexture_acg_index = IntProperty(default=0)


def unregister():
    for prop in ("minitexture_acg_results", "minitexture_acg_index"):
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
