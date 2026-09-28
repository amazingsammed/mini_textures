# Mini Texture — Blender Add-on

Mini Texture is a self-contained texture toolkit for Blender. It ships a bundle of
**CC0 PBR materials**, lets you **browse CC0 texture websites** from inside Blender,
**download CC0 materials** without leaving the app, and **build fully wired PBR
materials** in one click. Everything is CC0, so the bundled content and anything you
download from the flagged sources is safe to use commercially and to redistribute.

- **Version:** 1.0.0
- **Blender:** 3.3 or newer (tested on 4.x and 5.0)
- **License of bundled content:** CC0 1.0 (public domain)

---

## Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick start](#quick-start)
4. [The sidebar panels](#the-sidebar-panels)
5. [PBR maps and how materials are built](#pbr-maps-and-how-materials-are-built)
6. [Bundled library](#bundled-library)
7. [Texture sites](#texture-sites)
8. [ambientCG downloader](#ambientcg-downloader)
9. [Importing your own textures](#importing-your-own-textures)
10. [Procedural materials](#procedural-materials)
11. [Licensing and selling](#licensing-and-selling)
12. [Troubleshooting](#troubleshooting)
13. [File structure](#file-structure)

---

## Features

- **50 bundled PBR materials**, each with diffuse, normal, displacement, ambient
  occlusion and roughness maps (plus metallic where available).
- **Texture Sites browser** — open or search 12 texture sources, with CC0
  resale-safe sites clearly marked.
- **ambientCG downloader** — search the ambientCG API and download CC0 materials
  (1K/2K/4K, JPG/PNG) straight into your library, maps auto-named.
- **One-click material builder** — assembles a complete Principled BSDF setup with
  AO multiplied into the albedo, a normal map, a displacement node, and roughness /
  metallic maps, then assigns it to the selected object.
- **Import tools** — add individual files or whole folders of textures.
- **Procedural materials** — instantly create Noise, Marble, Wood or Rust materials
  with no image files.
- **In-addon Help panel** and this documentation.

---

## Installation

1. In Blender, open **Edit ▸ Preferences ▸ Add-ons**.
2. Click the dropdown arrow (top-right) and choose **Install from Disk**.
3. Select `Mini_Texture_1.0.0.zip` and confirm.
4. Enable the **Mini Texture** add-on in the list (checkbox).
5. In the 3D Viewport press **N** to open the sidebar, then click the
   **Mini Texture** tab.

To update, install the newer zip over the top (keep *overwrite* enabled) and reopen
Blender.

---

## Quick start

1. Open the **My Textures** panel.
2. Pick a category and click any thumbnail — a full PBR material is created and
   assigned to the selected object.
3. Looking for something specific? Search on **ambientCG** (downloads inside
   Blender) or browse **Texture Sites** to download manually.
4. Have your own maps? Add them in **Tools**.

> **Tip:** With an object selected, the built material is assigned automatically.
> Turn off *Apply to selected object* in the **My Textures** panel to only create
> the material without assigning it.

---

## The sidebar panels

| Panel | Purpose |
| --- | --- |
| **My Textures** | The bundled + imported library. Filter by category, then click a thumbnail to build and apply the material. |
| **ambientCG Downloader (CC0)** | Search ambientCG and download full PBR sets into your library. |
| **Tools** | Import files/folders and create procedural materials. |
| **Help / Docs** | Short usage notes and a button to open this file. |
| **Texture Sites** | Browse / search external CC0 texture websites. |

Panels are ordered so the **Texture Sites** browser is last.

---

## PBR maps and how materials are built

Each material can contain these maps. They are detected automatically by the file
name suffix (for example `brick_red_diffuse.jpg`, `brick_red_normal.jpg`):

| Kind | Recognised suffixes | Used for |
| --- | --- | --- |
| Diffuse | `_diffuse`, `_diff`, `_albedo`, `_col`, `_color`, `_basecolor` | Base Color |
| Normal | `_normal`, `_nrm`, `_nor`, `_normalgl`, `_normaldx` | Normal Map node |
| Displacement | `_displacement`, `_disp`, `_height` | Displacement node |
| Ambient occlusion | `_ao`, `_ambientocclusion`, `_occlusion` | Multiplied into Base Color |
| Roughness | `_roughness`, `_rough`, `_rgh` | Roughness |
| Metallic | `_metallic`, `_metalness` | Metallic |

When you click a texture, Mini Texture builds a Principled BSDF material and:

- multiplies **diffuse × AO** into the Base Color,
- feeds the **normal map** through a Normal Map node,
- feeds the **displacement** through a Displacement node into the Material Output
  (the material's displacement method is set to *Displacement*),
- connects **roughness** and **metallic** maps when present,
- adds a shared UV/Mapping node so you can scale the tiling from one place.

**About displacement:** the Displacement node affects **Cycles** and needs enough
mesh geometry (subdivide the object or add a Subdivision Surface modifier). For a
fast surface impression without geometry, rely on the normal map. EEVEE uses the
normal map; true displacement is a Cycles feature.

---

## Bundled library

50 materials ship with the add-on (all CC0):

- **Generated by Mini Texture (38):** fabric_canvas, concrete_wall, metal_rust,
  wood_planks, grass_field, marble_white, brick_red, sand_desert, dirt_ground,
  leather_brown, camouflage, checker_grid, tiles_ceramic, rock_granite,
  metal_brushed, metal_gold, metal_copper, metal_galvanized, asphalt_road,
  gravel_ground, snow_ground, moss_ground, wood_walnut, wood_pine,
  wood_dark_planks, linen_white, carpet_fabric, denim_blue, cobblestone,
  plaster_wall, terracotta, marble_black, obsidian, hazard_stripes,
  water_ripples, scales_reptile, lava_flow, cardboard.
- **Photogrammetry from ambientCG (12):** Bricks105, Concrete034, Ground111,
  Grass005, Marble012, Metal063, PavingStones151, Rock064, Tiles141, Wood095,
  WoodFloor051, Asphalt033.

Every item has diffuse, normal, displacement and roughness; most also have AO, and
the metal sets include a metallic map.

---

## Texture sites

The **Texture Sites** panel opens each source in your browser and can run a search
using the text in the search box. The **checkmark** marks sources whose license is
**safe to resell / redistribute**.

| Site | License | Resale-safe |
| --- | --- | --- |
| Poly Haven | CC0 | Yes |
| ambientCG | CC0 | Yes |
| 3D Textures | CC0 | Yes |
| CGBookcase | CC0 | Yes |
| ShareTextures | CC0 | Yes |
| Texture Ninja | CC0 | Yes |
| NASA Image Library | Public domain | Yes |
| PublicDomainPictures | Public domain (CC0) | Yes |
| OpenGameArt | Mixed (CC0 / CC-BY) | Check each file |
| Wikimedia Commons | Mixed (PD / CC) | Check each file |
| Pixabay | Pixabay License | No (do not resell raw copies) |
| Unsplash | Unsplash License | No (do not resell raw copies) |

Buttons:

- **Search All Resale-Safe Sites** — opens a search for your query on the
  CC0/public-domain sites (up to six tabs).
- **Search One** — opens a search on the site chosen in the dropdown.
- Clicking a site name opens its home page.

---

## ambientCG downloader

1. Type a query (e.g. `brick`) in the search box.
2. Press **Search ambientCG** — up to 24 results are listed.
3. Select a result, choose **Resolution** (1K/2K/4K) and **Format** (JPG/PNG).
4. Press **Download** — the set is fetched, unzipped into your library folder, and
   its maps are renamed to `_diffuse`, `_normal`, `_displacement`, `_ao`,
   `_roughness`, `_metallic`.
5. Press **Refresh** in **My Textures** (it usually refreshes automatically).

`Open Page` opens the asset page in your browser for reference.

---

## Importing your own textures

- **Import Files** — choose one or more images; they are copied into your library.
- **Import Folder** *(Tools)* — point at a downloaded folder and import it in bulk.

Suffix your files with `_diffuse`, `_normal`, `_displacement`, `_ao`,
`_roughness`, `_metallic` so they are recognised as one material. Files without a
suffix are treated as diffuse.

Your downloads and imports live in the folder shown in
**Edit ▸ Preferences ▸ Add-ons ▸ Mini Texture ▸ My Library Folder**. Leave it blank
to use Blender's user data folder.

---

## Procedural materials

In **Tools ▸ Procedural materials**, click **Noise**, **Marble**, **Wood** or
**Rust** to create a fully procedural material (no image files) with a Noise
texture, ColorRamp and Bump, assigned to the selected object. Great for quick
look-dev and for surfaces you never need to texture by hand.

---

## Licensing and selling

- **Bundled generated textures:** created by Mini Texture and released as **CC0**.
- **Bundled ambientCG materials:** ambientCG publishes its assets under **CC0**.
- **CC0** places the work in the public domain: no attribution is required and you
  may use, modify, redistribute and sell it.

You can therefore safely include the bundled library in a product you sell. Only
use the sites marked *Resale-safe* above if you intend to redistribute what you
download. Pixabay and Unsplash are free for many uses but their licenses do **not**
allow reselling unaltered copies.

This documentation is not legal advice; always confirm the license on the source
page.

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| No thumbnails in the panel | In `--background` mode Blender cannot generate previews — this is normal. In the GUI they appear automatically. Press **Refresh** if needed. |
| Downloaded textures don't appear | Press **Refresh** in *My Textures*, and confirm the My Library Folder is set as expected. |
| "Network error" when searching ambientCG | Check your internet connection/proxy. You can still download manually via Texture Sites. |
| Displacement looks flat | Displacement needs Cycles and geometry — add a Subdivision Surface modifier to the object. |
| Material not assigned | Enable *Apply to selected object* and make sure a mesh object is selected. |
| Add-on won't enable | Confirm the Blender version is 3.3 or newer and that you installed the `.zip`, not the folder. |

---

## File structure

```
mini_texture/
├── __init__.py          # add-on registration (bl_info)
├── ui.py                # sidebar panels (My Textures, ambientCG, Tools, Help, Sites)
├── operators.py         # material builder, import, apply, procedural, open docs
├── library.py           # library scan + preview icons
├── downloads.py         # ambientCG search + download
├── properties.py        # scene properties
├── preferences.py       # add-on preferences (library folder)
├── sites.py             # texture site registry
├── README.md            # this documentation
├── textures/            # bundled PBR maps (CC0)
└── thumbs/              # 128px preview thumbnails
```

---

*Mini Texture 1.0.0 — bundled textures CC0 1.0. Have fun creating.*
