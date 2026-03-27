from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


PROFILE_REPO = Path(__file__).resolve().parents[1]
README_PATH = PROFILE_REPO / "README.md"
START_MARKER = "<!--LATEST_SECTION_START-->"
END_MARKER = "<!--LATEST_SECTION_END-->"

REPOS = [
    "ai-career-transition-roadmap",
    "multi-agent-system-basics",
    "prompt-engineering-foundations",
    "llm-evals-and-anti-hallucination",
    "cursor-ai-development-workflows",
    "agent-architecture-patterns",
]


def github_get(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dhirajkrsingh-profile-readme-updater",
            **(
                {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
                if os.environ.get("GITHUB_TOKEN")
                else {}
            ),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fetch_repo(repo_name: str) -> dict:
    return github_get(f"https://api.github.com/repos/dhirajkrsingh/{repo_name}")


def render_latest_section(repos: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%d %b %Y")
    lines = [
        "## Latest",
        "",
        f"Updated automatically on {now} from the flagship repositories.",
        "",
    ]
    for repo in repos[:3]:
        pushed = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00")).strftime("%d %b %Y")
        lines.append(
            f"- **{pushed}** — [{repo['name']}](https://github.com/dhirajkrsingh/{repo['name']})"
            f" — {repo['description']}"
        )
    lines.extend(
        [
            "",
            "Current emphasis: applied showcase work, reliability-first workflows, and structured AI learning paths.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    repos = sorted((fetch_repo(name) for name in REPOS), key=lambda repo: repo["pushed_at"], reverse=True)
    latest = render_latest_section(repos)
    replacement = f"{START_MARKER}\n{latest}\n{END_MARKER}"
    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError("Latest section markers were not found in README.md")
    start_index = readme.index(START_MARKER)
    end_index = readme.index(END_MARKER) + len(END_MARKER)
    updated = readme[:start_index] + replacement + readme[end_index:]
    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()