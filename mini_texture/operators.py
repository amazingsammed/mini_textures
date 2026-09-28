"""Operators for browsing sites, importing and applying textures."""

import os
import shutil
import subprocess
import sys

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import Operator, OperatorFileListElement

try:
    from . import library, sites
except ImportError:
    import library
    import sites


# --------------------------------------------------------------------- helpers
def _open_url(url):
    try:
        bpy.ops.wm.url_open(url=url)
        return True
    except Exception:
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception:
            return False


def _load_image(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return img


def _build_material(name, item):
    files = item["files"]
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (250, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    x = -400
    diffuse_tex = None
    if "diffuse" in files:
        diffuse_tex = nt.nodes.new("ShaderNodeTexImage")
        diffuse_tex.location = (x, 250)
        diffuse_tex.image = _load_image(files["diffuse"])
        x -= 300

    # Ambient occlusion darkens the albedo (diffuse * ao)
    if "ao" in files:
        ao_tex = nt.nodes.new("ShaderNodeTexImage")
        ao_tex.location = (x, 500)
        ao_tex.image = _load_image(files["ao"], non_color=True)
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.location = (-150, 300)
        mix.inputs["Fac"].default_value = 1.0
        if diffuse_tex:
            nt.links.new(diffuse_tex.outputs["Color"], mix.inputs["Color1"])
        nt.links.new(ao_tex.outputs["Color"], mix.inputs["Color2"])
        nt.links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
        x -= 300
    elif diffuse_tex:
        nt.links.new(diffuse_tex.outputs["Color"], bsdf.inputs["Base Color"])

    if "roughness" in files:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (x, 0)
        tex.image = _load_image(files["roughness"], non_color=True)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])
    else:
        bsdf.inputs["Roughness"].default_value = 0.8

    if "metallic" in files:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (x, -250)
        tex.image = _load_image(files["metallic"], non_color=True)
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Metallic"])
    else:
        bsdf.inputs["Metallic"].default_value = (
            1.0 if item.get("category") == "Metal" else 0.0
        )

    if "normal" in files:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (x, -500)
        tex.image = _load_image(files["normal"], non_color=True)
        nrm = nt.nodes.new("ShaderNodeNormalMap")
        nrm.location = (0, -500)
        nt.links.new(tex.outputs["Color"], nrm.inputs["Color"])
        nt.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])

    if "displacement" in files:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.location = (x, -750)
        tex.image = _load_image(files["displacement"], non_color=True)
        disp = nt.nodes.new("ShaderNodeDisplacement")
        disp.location = (250, -350)
        try:
            disp.inputs["Midlevel"].default_value = 0.5
            disp.inputs["Scale"].default_value = 0.05
        except Exception:
            pass
        nt.links.new(tex.outputs["Color"], disp.inputs["Height"])
        nt.links.new(disp.outputs["Displacement"], out.inputs["Displacement"])
        for target in (mat, getattr(mat, "cycles", None)):
            try:
                target.displacement_method = "DISPLACEMENT"
            except Exception:
                pass

    # UV mapping so textures tile with the node's scale
    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-1050, -100)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-800, -100)
    nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])
    for node in nt.nodes:
        if node.type in {"TEX_IMAGE", "TEX_NOISE", "TEX_VORONOI"}:
            for inp in node.inputs:
                if inp.name == "Vector" and not inp.is_linked:
                    nt.links.new(mapping.outputs["Vector"], inp)

    return mat


def _assign_to_selection(mat):
    targets = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    if not targets and bpy.context.active_object and bpy.context.active_object.type == "MESH":
        targets = [bpy.context.active_object]
    for obj in targets:
        if mat.name not in [m.name for m in obj.data.materials if m]:
            obj.data.materials.append(mat)
        else:
            for i, m in enumerate(obj.data.materials):
                if m and m.name == mat.name:
                    obj.active_material_index = i
    return len(targets)


# ----------------------------------------------------------------- site browse
class MINTEXTURE_OT_open_site(Operator):
    bl_idname = "minitexture.open_site"
    bl_label = "Open Site"
    bl_description = "Open this texture source in your web browser"

    site_id: StringProperty(default="")
    use_search: BoolProperty(default=False)

    def execute(self, context):
        if self.site_id:
            site = sites.by_id(self.site_id)
        else:
            site = sites.by_id(context.scene.minitexture_site)
        if not site:
            self.report({"ERROR"}, "Unknown site")
            return {"CANCELLED"}
        query = context.scene.minitexture_query if self.use_search else ""
        url = sites.resolved_url(site, query)
        if _open_url(url):
            self.report({"INFO"}, "Opened " + site["name"])
            return {"FINISHED"}
        self.report({"ERROR"}, "Could not open browser")
        return {"CANCELLED"}


class MINTEXTURE_OT_search_all(Operator):
    bl_idname = "minitexture.search_all"
    bl_label = "Search All Resale-Safe Sites"
    bl_description = "Open a search on every CC0 / public-domain source"

    def execute(self, context):
        query = context.scene.minitexture_query.strip()
        opened = 0
        for s in sites.SITES:
            if not s.get("resale"):
                continue
            if not s.get("search"):
                continue
            _open_url(sites.resolved_url(s, query))
            opened += 1
            if opened >= 6:  # avoid opening dozens of tabs
                break
        self.report({"INFO"}, "Opened %d searches" % opened)
        return {"FINISHED"}


# ------------------------------------------------------------------- importing
class MINTEXTURE_OT_import_folder(Operator):
    bl_idname = "minitexture.import_folder"
    bl_label = "Import Folder"
    bl_description = "Copy every texture in the chosen folder into My Library"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        src = bpy.path.abspath(context.scene.minitexture_import_path)
        if not src or not os.path.isdir(src):
            self.report({"ERROR"}, "Choose a valid folder first")
            return {"CANCELLED"}
        dest = os.path.join(library.user_dir(), os.path.basename(src.rstrip("\\/")) or "imported")
        count = 0
        for root, _dirs, files in os.walk(src):
            rel = os.path.relpath(root, src)
            target = os.path.join(dest, rel) if rel != "." else dest
            os.makedirs(target, exist_ok=True)
            for f in files:
                if os.path.splitext(f)[1].lower() in library.IMAGE_EXTS:
                    shutil.copy2(os.path.join(root, f), os.path.join(target, f))
                    count += 1
        library.refresh()
        self.report({"INFO"}, "Imported %d files" % count)
        return {"FINISHED"}


class MINTEXTURE_OT_import_files(Operator):
    bl_idname = "minitexture.import_files"
    bl_label = "Import Files"
    bl_description = "Add selected image files to My Library"
    bl_options = {"REGISTER", "UNDO"}

    files: CollectionProperty(type=OperatorFileListElement)
    directory: StringProperty(subtype="DIR_PATH")

    filter_image = True
    filter_glob: StringProperty(
        default="*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.bmp;*.webp;*.exr",
        options={"HIDDEN"},
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        dest = os.path.join(library.user_dir(), "imported")
        os.makedirs(dest, exist_ok=True)
        count = 0
        for f in self.files:
            src = os.path.join(self.directory, f.name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest, f.name))
                count += 1
        library.refresh()
        self.report({"INFO"}, "Imported %d files" % count)
        return {"FINISHED"}


class MINTEXTURE_OT_import_selected(Operator):
    bl_idname = "minitexture.import_selected"
    bl_label = "Import Selected"
    bl_description = "Import the highlighted files into My Library"
    bl_options = {"REGISTER", "UNDO"}

    keys: StringProperty(default="")

    def execute(self, context):
        dest = os.path.join(library.user_dir(), "imported")
        os.makedirs(dest, exist_ok=True)
        count = 0
        for path in self.keys.split("|"):
            if path and os.path.isfile(path):
                shutil.copy2(path, os.path.join(dest, os.path.basename(path)))
                count += 1
        library.refresh()
        self.report({"INFO"}, "Imported %d files" % count)
        return {"FINISHED"}


# ------------------------------------------------------------------- applying
class MINTEXTURE_OT_apply(Operator):
    bl_idname = "minitexture.apply"
    bl_label = "Apply Texture"
    bl_description = "Build a PBR material from this texture"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(default="")

    def execute(self, context):
        name = self.name or context.scene.minitexture_enum
        item = library.get(name)
        if not item:
            self.report({"ERROR"}, "Texture not found")
            return {"CANCELLED"}
        mat = _build_material(item["name"], item)
        if context.scene.minitexture_auto_apply:
            n = _assign_to_selection(mat)
            if n:
                self.report({"INFO"}, "Applied to %d object(s)" % n)
            else:
                self.report({"INFO"}, "Material '%s' created" % mat.name)
        else:
            self.report({"INFO"}, "Material '%s' created" % mat.name)
        return {"FINISHED"}


class MINTEXTURE_OT_refresh(Operator):
    bl_idname = "minitexture.refresh"
    bl_label = "Refresh Library"
    bl_description = "Rescan the texture library"

    def execute(self, context):
        library.clear_previews()
        items = library.refresh()
        self.report({"INFO"}, "%d textures" % len(items))
        return {"FINISHED"}


# ----------------------------------------------------------------- documentation
class MINTEXTURE_OT_open_docs(Operator):
    bl_idname = "minitexture.open_docs"
    bl_label = "Open Documentation"
    bl_description = "Open the bundled README documentation file"

    def execute(self, context):
        candidates = (
            os.path.join(os.path.dirname(__file__), "README.md"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md"),
        )
        for path in candidates:
            if os.path.isfile(path):
                try:
                    if hasattr(os, "startfile"):
                        os.startfile(path)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", path])
                    else:
                        subprocess.Popen(["xdg-open", path])
                    self.report({"INFO"}, "Opened documentation")
                    return {"FINISHED"}
                except Exception as exc:
                    self.report({"ERROR"}, "Could not open: %s" % exc)
                    return {"CANCELLED"}
        self.report({"ERROR"}, "Documentation file not found")
        return {"CANCELLED"}


# ----------------------------------------------------------------- procedural
class MINTEXTURE_OT_procedural(Operator):
    bl_idname = "minitexture.procedural"
    bl_label = "Add Procedural Texture"
    bl_description = "Create a seamless procedural detail material (no image files)"
    bl_options = {"REGISTER", "UNDO"}

    kind: EnumProperty(
        name="Type",
        items=[
            ("NOISE", "Noise / Organic", ""),
            ("MARBLE", "Marble", ""),
            ("WOOD", "Wood", ""),
            ("RUST", "Rust / Corrosion", ""),
        ],
        default="NOISE",
    )

    def execute(self, context):
        mat = bpy.data.materials.new("Procedural " + self.kind.title())
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()

        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (800, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (500, 0)
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        coord = nt.nodes.new("ShaderNodeTexCoord")
        coord.location = (-900, 0)
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.location = (-700, 0)
        nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.location = (-450, 100)
        nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.location = (-150, 150)
        nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])

        bump = nt.nodes.new("ShaderNodeBump")
        bump.location = (200, -250)
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

        if self.kind == "MARBLE":
            noise.inputs["Scale"].default_value = 6.0
            noise.inputs["Detail"].default_value = 6.0
            ramp.color_ramp.elements[0].position = 0.35
            ramp.color_ramp.elements[0].color = (0.9, 0.9, 0.92, 1)
            ramp.color_ramp.elements[1].position = 0.65
            ramp.color_ramp.elements[1].color = (0.25, 0.25, 0.3, 1)
            bsdf.inputs["Roughness"].default_value = 0.2
        elif self.kind == "WOOD":
            noise.inputs["Scale"].default_value = 3.0
            noise.inputs["Detail"].default_value = 8.0
            ramp.color_ramp.elements[0].position = 0.4
            ramp.color_ramp.elements[0].color = (0.42, 0.22, 0.08, 1)
            ramp.color_ramp.elements[1].position = 0.75
            ramp.color_ramp.elements[1].color = (0.72, 0.47, 0.22, 1)
            bsdf.inputs["Roughness"].default_value = 0.6
        elif self.kind == "RUST":
            noise.inputs["Scale"].default_value = 12.0
            noise.inputs["Detail"].default_value = 10.0
            ramp.color_ramp.elements[0].position = 0.3
            ramp.color_ramp.elements[0].color = (0.3, 0.28, 0.26, 1)
            ramp.color_ramp.elements[1].position = 0.7
            ramp.color_ramp.elements[1].color = (0.55, 0.18, 0.05, 1)
            bsdf.inputs["Metallic"].default_value = 0.6
            bsdf.inputs["Roughness"].default_value = 0.8
        else:
            bsdf.inputs["Roughness"].default_value = 0.7

        _assign_to_selection(mat)
        self.report({"INFO"}, "Created '%s'" % mat.name)
        return {"FINISHED"}


CLASSES = (
    MINTEXTURE_OT_open_site,
    MINTEXTURE_OT_search_all,
    MINTEXTURE_OT_import_folder,
    MINTEXTURE_OT_import_files,
    MINTEXTURE_OT_import_selected,
    MINTEXTURE_OT_apply,
    MINTEXTURE_OT_refresh,
    MINTEXTURE_OT_open_docs,
    MINTEXTURE_OT_procedural,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
