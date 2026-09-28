"""Sidebar UI for the Mini Texture add-on."""

import bpy
from bpy.types import Panel, UIList

try:
    from . import library, sites
except ImportError:
    import library
    import sites

CATEGORY = "Mini Texture"


class MINTEXTURE_UL_acg(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_prop, index):
        row = layout.row(align=True)
        row.label(text=item.name)
        row.label(text=item.asset_id, icon="IMAGE_REFERENCE")


class MINTEXTURE_PT_sites(Panel):
    bl_label = "Texture Sites"
    bl_idname = "MINTEXTURE_PT_sites"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_order = 100

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.prop(scene, "minitexture_query", text="", icon="VIEWZOOM")
        row = col.row(align=True)
        row.operator("minitexture.search_all", icon="WORLD")
        row.operator("minitexture.open_site", text="Search One", icon="URL").use_search = True

        layout.separator()
        box = layout.box()
        box.label(text="Open a source:", icon="BOOKMARKS")
        for site in sites.SITES:
            row = box.row(align=True)
            row.scale_y = 1.1
            op = row.operator(
                "minitexture.open_site",
                text=site["name"],
                icon="CHECKMARK" if site.get("resale") else "ERROR",
            )
            op.site_id = site["id"]
            op.use_search = False

        layout.separator()
        warn = layout.box()
        warn.label(text="Resale check:", icon="INFO")
        warn.label(text="Only sources marked with a check")
        warn.label(text="are CC0 / public domain and safe to")
        warn.label(text="redistribute or sell.")


class MINTEXTURE_PT_ambientcg(Panel):
    bl_label = "ambientCG Downloader (CC0)"
    bl_idname = "MINTEXTURE_PT_ambientcg"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_order = 1
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)
        col.prop(scene, "minitexture_query", text="", icon="VIEWZOOM")
        col.operator("minitexture.acg_search", icon="VIEWZOOM")

        if scene.minitexture_acg_results:
            layout.template_list(
                "MINTEXTURE_UL_acg", "",
                scene, "minitexture_acg_results",
                scene, "minitexture_acg_index",
                rows=6,
            )
            row = layout.row(align=True)
            row.operator("minitexture.acg_open_page", icon="URL")
            dl = row.operator("minitexture.acg_download", text="Download", icon="IMPORT")
        else:
            layout.label(text="Search, pick a result, download.")


class MINTEXTURE_PT_library(Panel):
    bl_label = "My Textures"
    bl_idname = "MINTEXTURE_PT_library"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
        row.prop(scene, "minitexture_category", text="")
        row.operator("minitexture.refresh", text="", icon="FILE_REFRESH")

        items = library.all_items()
        cat = scene.minitexture_category
        shown = [it for it in items if cat == "ALL" or it["category"] == cat]
        if not shown:
            layout.label(text="No textures found.", icon="INFO")
            return

        layout.prop(scene, "minitexture_auto_apply")

        flow = layout.column_flow(columns=3, align=True)
        for it in shown:
            box = flow.box()
            col = box.column(align=True)
            if it["icon"]:
                col.template_icon(icon_value=it["icon"], scale=3.0)
            else:
                col.label(icon="FILE_IMAGE")
            op = col.operator("minitexture.apply", text=it["name"])
            op.name = it["name"]


class MINTEXTURE_PT_tools(Panel):
    bl_label = "Tools"
    bl_idname = "MINTEXTURE_PT_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column(align=True)
        col.operator("minitexture.import_files", icon="FILE_IMAGE")
        col.prop(scene, "minitexture_import_path", text="")
        col.operator("minitexture.import_folder", icon="FILE_FOLDER")

        layout.separator()
        box = layout.box()
        box.label(text="Procedural materials:", icon="NODE_MATERIAL")
        row = box.row(align=True)
        for kind in ("NOISE", "MARBLE", "WOOD", "RUST"):
            op = row.operator("minitexture.procedural", text=kind.title())
            op.kind = kind


class MINTEXTURE_PT_help(Panel):
    bl_label = "Help / Docs"
    bl_idname = "MINTEXTURE_PT_help"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CATEGORY
    bl_order = 3
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Quick start:")
        col.label(text="1. Open 'My Textures'")
        col.label(text="2. Click a thumbnail to")
        col.label(text="   build a PBR material")
        col.label(text="3. Search CC0 sources in")
        col.label(text="   'ambientCG' / 'Texture Sites'")
        col.label(text="4. Import your own maps in 'Tools'")

        layout.separator()
        box = layout.box()
        box.label(text="Each material ships:", icon="IMAGE_DATA")
        box.label(text="diffuse, normal, displacement,")
        box.label(text="AO and roughness (metallic too).")

        layout.separator()
        layout.operator("minitexture.open_docs", icon="HELP")


CLASSES = (
    MINTEXTURE_UL_acg,
    MINTEXTURE_PT_library,
    MINTEXTURE_PT_ambientcg,
    MINTEXTURE_PT_tools,
    MINTEXTURE_PT_help,
    MINTEXTURE_PT_sites,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
