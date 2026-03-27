from __future__ import annotations

import base64
import json
import os
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER_API = "https://api.github.com/users/dhirajkrsingh"


def fetch_image_base64(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "dhirajkrsingh-profile-hero-generator"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return base64.b64encode(response.read()).decode("ascii")


def fetch_avatar_url() -> str:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "dhirajkrsingh-profile-hero-generator",
    }
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    request = urllib.request.Request(USER_API, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    return payload["avatar_url"]


def hero_svg(theme: str, photo_data: str) -> str:
    if theme == "light":
        bg_start = "#F6F8FC"
        bg_end = "#EAF2FF"
        panel = "rgba(255,255,255,0.84)"
        panel_stroke = "#D8E6FF"
        heading = "#0F172A"
        body = "#334155"
        muted = "#475569"
        accent_a = "#0A7EA4"
        accent_b = "#165DFF"
        accent_c = "#0F9D58"
        chip_bg = "#F8FAFC"
    else:
        bg_start = "#09111F"
        bg_end = "#0A1A2A"
        panel = "rgba(15,23,42,0.84)"
        panel_stroke = "#1E293B"
        heading = "#F8FAFC"
        body = "#CBD5E1"
        muted = "#94A3B8"
        accent_a = "#5EEAD4"
        accent_b = "#60A5FA"
        accent_c = "#A78BFA"
        chip_bg = "#0B1220"

    return f'''<svg width="1280" height="420" viewBox="0 0 1280 420" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Dhiraj Singh portrait hero</title>
  <desc id="desc">Theme-aware GitHub profile hero with Dhiraj Singh portrait, AI learning systems focus, and flagship track callouts.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1280" y2="420" gradientUnits="userSpaceOnUse">
      <stop stop-color="{bg_start}"/>
      <stop offset="1" stop-color="{bg_end}"/>
    </linearGradient>
    <linearGradient id="ring" x1="140" y1="60" x2="1160" y2="360" gradientUnits="userSpaceOnUse">
      <stop stop-color="{accent_a}"/>
      <stop offset="0.5" stop-color="{accent_b}"/>
      <stop offset="1" stop-color="{accent_c}"/>
    </linearGradient>
    <clipPath id="portraitClip">
      <circle cx="250" cy="210" r="120"/>
    </clipPath>
  </defs>
  <rect width="1280" height="420" rx="28" fill="url(#bg)"/>
  <circle cx="1160" cy="92" r="112" fill="{accent_b}" fill-opacity="0.10"/>
  <circle cx="1104" cy="318" r="84" fill="{accent_c}" fill-opacity="0.10"/>
  <rect x="56" y="40" width="1168" height="340" rx="30" fill="{panel}" stroke="{panel_stroke}"/>
  <circle cx="250" cy="210" r="132" fill="url(#ring)"/>
  <circle cx="250" cy="210" r="122" fill="#0F172A" fill-opacity="0.18"/>
  <image href="data:image/png;base64,{photo_data}" x="130" y="90" width="240" height="240" clip-path="url(#portraitClip)" preserveAspectRatio="xMidYMid slice"/>
  <text x="430" y="118" fill="{accent_b}" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="700" letter-spacing="0.12em">DHIRAJ SINGH</text>
  <text x="430" y="176" fill="{heading}" font-family="Segoe UI, Arial, sans-serif" font-size="46" font-weight="800">AI Learning Systems</text>
  <text x="430" y="226" fill="{body}" font-family="Segoe UI, Arial, sans-serif" font-size="28" font-weight="600">Prompt Reliability • Multi-Agent Systems • Career Transition</text>
  <text x="430" y="270" fill="{muted}" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="500">Structured paths, practical assets, and reliability-first workflows through VAIU Research Lab.</text>
  <rect x="430" y="292" width="332" height="8" rx="4" fill="url(#ring)"/>

  <rect x="830" y="104" width="304" height="52" rx="14" fill="{chip_bg}" stroke="{accent_b}"/>
  <text x="856" y="137" fill="{accent_b}" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="700">Career Roadmaps</text>

  <rect x="864" y="176" width="270" height="52" rx="14" fill="{chip_bg}" stroke="{accent_c}"/>
  <text x="890" y="209" fill="{accent_c}" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="700">Prompt Reliability</text>

  <rect x="796" y="248" width="338" height="52" rx="14" fill="{chip_bg}" stroke="{accent_a}"/>
  <text x="822" y="281" fill="{accent_a}" font-family="Segoe UI, Arial, sans-serif" font-size="20" font-weight="700">Agent Systems Track</text>
</svg>
'''


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    photo_data = fetch_image_base64(fetch_avatar_url())
    (ASSETS / "hero-light.svg").write_text(hero_svg("light", photo_data), encoding="utf-8")
    (ASSETS / "hero-dark.svg").write_text(hero_svg("dark", photo_data), encoding="utf-8")


if __name__ == "__main__":
    main()