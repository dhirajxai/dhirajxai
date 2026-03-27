from __future__ import annotations

import io
import json
import os
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER_API = "https://api.github.com/users/dhirajkrsingh"

# Dark-to-light: dense chars represent dark pixels, spaces represent light.
_ASCII_RAMP = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "


def fetch_user_data() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "dhirajkrsingh-profile-hero-generator",
    }
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    req = urllib.request.Request(USER_API, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_image_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "dhirajkrsingh-profile-hero-generator"}
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def image_to_ascii(img_bytes: bytes, cols: int = 48, aspect: float = 0.55) -> list[str]:
    """Convert image to ASCII art with proper aspect-ratio correction.

    Monospace glyphs are taller than wide (~1.8:1). *aspect* compensates so
    the output looks square rather than stretched vertically.
    """
    img = Image.open(io.BytesIO(img_bytes)).convert("L")
    w, h = img.size
    cell_w = w / cols
    cell_h = cell_w / aspect          # taller cells → fewer rows
    rows = int(h / cell_h)
    img = img.resize((cols, rows), Image.LANCZOS)

    ramp = _ASCII_RAMP
    n = len(ramp) - 1
    return [
        "".join(ramp[int(img.getpixel((x, y)) / 255 * n)] for x in range(cols))
        for y in range(rows)
    ]


def _x(s: str) -> str:
    """Escape XML special characters."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


def _text(x, y, fill, content, size="11", weight="normal"):
    return (
        f'  <text x="{x}" y="{y}"'
        f' font-family="\'Courier New\', Courier, monospace"'
        f' font-size="{size}" font-weight="{weight}"'
        f' fill="{fill}" xml:space="preserve">{_x(content)}</text>'
    )


def _kv(x, y, dim, key_col, key, dots_col, dots, val_col, val):
    """Render a coloured key: ... value row using tspan."""
    return (
        f'  <text x="{x}" y="{y}"'
        f' font-family="\'Courier New\', Courier, monospace"'
        f' font-size="11" xml:space="preserve">'
        f'<tspan fill="{dim}">. </tspan>'
        f'<tspan fill="{key_col}" font-weight="bold">{_x(key)}:</tspan>'
        f'<tspan fill="{dots_col}"> {_x(dots)} </tspan>'
        f'<tspan fill="{val_col}">{_x(val)}</tspan>'
        f'</text>'
    )


def neofetch_svg(theme: str, ascii_lines: list[str], user: dict) -> str:
    if theme == "dark":
        bg         = "#0D1117"
        border     = "#30363D"
        titlebar   = "#161B22"
        dim        = "#6E7681"
        key_col    = "#FF7B72"
        val_col    = "#C9D1D9"
        header_col = "#58A6FF"
        lab_col    = "#D2A8FF"
        green_col  = "#E6EDF3"
        stats_col  = "#FFA657"
        hi_col     = "#79C0FF"
        palette    = ["#FF5F57","#FFBD2E","#28C840","#58A6FF","#D2A8FF","#FFA657","#79C0FF","#A5F3FC"]
    else:
        bg         = "#F6F8FA"
        border     = "#D0D7DE"
        titlebar   = "#EAEEF2"
        dim        = "#656D76"
        key_col    = "#CF222E"
        val_col    = "#24292F"
        header_col = "#0969DA"
        lab_col    = "#8250DF"
        green_col  = "#1F2328"
        stats_col  = "#9A6700"
        hi_col     = "#0550AE"
        palette    = ["#FF5F57","#FFBD2E","#28C840","#0969DA","#8250DF","#9A6700","#0550AE","#0E7490"]

    W, H  = 960, 460
    CW    = 6.45   # monospace char width @ 11px Courier New
    LH    = 14.0   # line height
    PAD_L = 24
    PAD_T = 54     # top of content area (below title bar)

    ascii_panel_w = max(len(ln) for ln in ascii_lines) * CW
    INFO_X = PAD_L + ascii_panel_w + 28
    COL    = 22    # column width for dot-leader calculation

    repos     = user.get("public_repos", 0)
    followers = user.get("followers",    0)

    def kv(y, key, val, vc=None):
        vc = vc or val_col
        prefix = f". {key}: "
        dots = "." * max(1, COL - len(prefix))
        return _kv(INFO_X, y, dim, key_col, key, dim, dots, vc, val)

    parts: list[str] = []

    # ── SVG root ──────────────────────────────────────────────────────────
    parts.append(
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"'
        f' xmlns="http://www.w3.org/2000/svg" role="img"'
        f' aria-label="Dhiraj Singh – neofetch profile card">'
    )

    # background
    parts.append(
        f'  <rect width="{W}" height="{H}" rx="12"'
        f' fill="{bg}" stroke="{border}" stroke-width="1.5"/>'
    )

    # ── title bar ─────────────────────────────────────────────────────────
    parts.append(f'  <rect x="0" y="0" width="{W}" height="38" rx="12" fill="{titlebar}"/>')
    parts.append(f'  <rect x="0" y="20" width="{W}" height="18" fill="{titlebar}"/>')
    for cx, fc in [(20, "#FF5F57"), (42, "#FFBD2E"), (64, "#28C840")]:
        parts.append(f'  <circle cx="{cx}" cy="19" r="7" fill="{fc}"/>')
    parts.append(
        f'  <text x="{W // 2}" y="25" text-anchor="middle"'
        f' font-family="\'Courier New\', Courier, monospace"'
        f' font-size="12" fill="{dim}">dhirajkrsingh@github \u2014 overview</text>'
    )

    # ── ASCII art (left panel, green) ─────────────────────────────────────
    for i, line in enumerate(ascii_lines):
        y = PAD_T + i * LH
        parts.append(_text(PAD_L, y, green_col, line))

    # ── info panel (right of ASCII art) ───────────────────────────────────
    iy = PAD_T + LH

    # username header
    parts.append(_text(INFO_X, iy, header_col, "dhirajsingh", size="13", weight="bold"))
    iy += LH

    # separator
    parts.append(_text(INFO_X, iy, dim, "\u2500" * 50))
    iy += LH * 1.3

    # identity rows
    parts.append(kv(iy, "Focus",     "AI Learning Systems",               vc=hi_col));    iy += LH
    parts.append(kv(iy, "Role",      "Researcher & Curriculum Architect"           ));    iy += LH
    parts.append(kv(iy, "Lab",       "VAIU Research Lab",                  vc=lab_col));  iy += LH
    parts.append(kv(iy, "Location",  "India"                                        ));   iy += LH * 1.5

    # technical rows
    parts.append(kv(iy, "Languages", "Python, Markdown, YAML"                       ));   iy += LH
    parts.append(kv(iy, "Tracks",    "Prompt Eng · Multi-Agent · Career", vc=hi_col)); iy += LH
    parts.append(kv(iy, "Tools",     "LLMs, RAG, Cursor AI, GitHub"                 ));   iy += LH
    parts.append(kv(iy, "Repos",     f"{repos} public repositories",       vc=stats_col)); iy += LH
    parts.append(kv(iy, "Followers", str(followers)                                  ));   iy += LH * 1.5

    # stats section sub-header
    parts.append(_text(INFO_X, iy, lab_col, "\u2500 GitHub Stats " + "\u2500" * 36))
    iy += LH * 1.4

    # colour palette swatches
    px = float(INFO_X)
    for pc in palette:
        parts.append(
            f'  <rect x="{px:.1f}" y="{iy - 11:.1f}"'
            f' width="18" height="18" rx="3" fill="{pc}"/>'
        )
        px += 22

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    user      = fetch_user_data()
    img_bytes = fetch_image_bytes(user["avatar_url"])
    ascii_art = image_to_ascii(img_bytes, cols=48)

    (ASSETS / "hero-dark.svg").write_text(
        neofetch_svg("dark",  ascii_art, user), encoding="utf-8"
    )
    (ASSETS / "hero-light.svg").write_text(
        neofetch_svg("light", ascii_art, user), encoding="utf-8"
    )
    print("Done — hero-dark.svg and hero-light.svg generated.")


if __name__ == "__main__":
    main()
