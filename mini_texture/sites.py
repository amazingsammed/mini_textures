"""Texture site registry.

Only sources whose license permits redistribution / commercial resale are
flagged ``resale=True`` (CC0 / Public Domain).  Others are included for
convenience but clearly marked so the user can respect their terms.
"""

SITES = [
    {
        "id": "polyhaven",
        "name": "Poly Haven",
        "home": "https://polyhaven.com/textures",
        "search": "https://polyhaven.com/textures?q={q}",
        "license": "CC0 (public domain)",
        "resale": True,
        "note": "Fully free, no attribution required. Safe to redistribute.",
    },
    {
        "id": "ambientcg",
        "name": "ambientCG",
        "home": "https://ambientcg.com/list?type=Material",
        "search": "https://ambientcg.com/list?q={q}",
        "license": "CC0 (public domain)",
        "resale": True,
        "note": "In-addon search + download is supported for this source.",
    },
    {
        "id": "3dtextures",
        "name": "3D Textures",
        "home": "https://3dtextures.me/",
        "search": "https://3dtextures.me/?s={q}",
        "license": "CC0 (public domain)",
        "resale": True,
        "note": "PBR sets. Check each post's license notice.",
    },
    {
        "id": "cgbookcase",
        "name": "CGBookcase",
        "home": "https://cgbookcase.com/textures/",
        "search": "https://cgbookcase.com/search?q={q}",
        "license": "CC0 (public domain)",
        "resale": True,
        "note": "Free CC0 texture library.",
    },
    {
        "id": "sharetextures",
        "name": "ShareTextures",
        "home": "https://www.sharetextures.com/textures",
        "search": "https://www.sharetextures.com/search?q={q}",
        "license": "CC0 (public domain)",
        "resale": True,
        "note": "Free CC0 PBR textures.",
    },
    {
        "id": "textureninja",
        "name": "Texture Ninja",
        "home": "https://texture.ninja/",
        "search": None,
        "license": "CC0 (public domain)",
        "resale": True,
        "note": "Large CC0 texture archive.",
    },
    {
        "id": "opengameart",
        "name": "OpenGameArt",
        "home": "https://opengameart.org/art-search-advanced?field_art_type_tid%5B%5D=9",
        "search": "https://opengameart.org/art-search-advanced?keys={q}&field_art_type_tid%5B%5D=9",
        "license": "Mixed (CC0 / CC-BY)",
        "resale": False,
        "note": "Filter by CC0. CC-BY requires attribution.",
    },
    {
        "id": "wikimedia",
        "name": "Wikimedia Commons",
        "home": "https://commons.wikimedia.org/wiki/Category:Textures",
        "search": "https://commons.wikimedia.org/w/index.php?search={q}+texture&title=Special:MediaSearch&type=image",
        "license": "Mixed (PD / CC)",
        "resale": False,
        "note": "Check the license on each file page.",
    },
    {
        "id": "nasa",
        "name": "NASA Image Library",
        "home": "https://images.nasa.gov/",
        "search": "https://images.nasa.gov/search?q={q}",
        "license": "Public Domain",
        "resale": True,
        "note": "Mostly public domain. Great for planets / surfaces.",
    },
    {
        "id": "publicdomainpictures",
        "name": "PublicDomainPictures",
        "home": "https://www.publicdomainpictures.net/en/hledej.php?hleda=texture",
        "search": "https://www.publicdomainpictures.net/en/hledej.php?hleda={q}",
        "license": "Public Domain (CC0)",
        "resale": True,
        "note": "Public domain photos and textures.",
    },
    {
        "id": "pixabay",
        "name": "Pixabay",
        "home": "https://pixabay.com/images/search/texture/",
        "search": "https://pixabay.com/images/search/{q}/",
        "license": "Pixabay License",
        "resale": False,
        "note": "Free to use, but do NOT resell unaltered copies.",
    },
    {
        "id": "unsplash",
        "name": "Unsplash",
        "home": "https://unsplash.com/s/photos/texture",
        "search": "https://unsplash.com/s/photos/{q}",
        "license": "Unsplash License",
        "resale": False,
        "note": "Free to use; reselling raw copies is not allowed.",
    },
]


def by_id(site_id):
    for s in SITES:
        if s["id"] == site_id:
            return s
    return None


def resolved_url(site, query):
    """Return the URL to open for a site, using the search template if a query
    is supplied and the site supports search."""
    query = (query or "").strip()
    if query and site.get("search"):
        from urllib.parse import quote_plus
        return site["search"].format(q=quote_plus(query))
    return site["home"]
