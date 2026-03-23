#!/usr/bin/env python3
"""Sync workshop wiki pages from configured GitHub repositories."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "workshops.json"
WORKSHOPS_DIR = ROOT / "workshops"
SYNC_REPORT_PATH = ROOT / "sync-report.json"

GITHUB_API = "https://api.github.com"
GITHUB_WEB = "https://github.com"

SECTION_BUCKETS = {
    "setup": ["prerequisite", "getting started", "setup", "installation"],
    "tasks": ["task", "exercise", "project description", "module", "assignment"],
    "testing": ["test", "submission", "deliverable", "checklist"],
    "troubleshooting": ["troubleshooting", "common issue", "help", "support"],
}


def load_workshops() -> List[Dict[str, str]]:
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def github_get_json(path: str) -> Tuple[Optional[Dict], Optional[str]]:
    req = Request(
        f"{GITHUB_API}{path}",
        headers={
            "User-Agent": "fullstack2026-course-wiki-sync",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload), None
    except HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except URLError as exc:
        return None, f"Network error: {exc.reason}"


def github_get_text(path: str, accept: str) -> Tuple[Optional[str], Optional[str]]:
    req = Request(
        f"{GITHUB_API}{path}",
        headers={
            "User-Agent": "fullstack2026-course-wiki-sync",
            "Accept": accept,
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace"), None
    except HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except URLError as exc:
        return None, f"Network error: {exc.reason}"


def normalize_links(markdown: str, repo: str, branch: str) -> str:
    blob_base = f"{GITHUB_WEB}/{repo}/blob/{branch}/"
    raw_base = f"https://raw.githubusercontent.com/{repo}/{branch}/"

    def rewrite_link(match: re.Match) -> str:
        text, url = match.group(1), match.group(2).strip()
        if url.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        normalized = url.lstrip("./")
        return f"[{text}]({blob_base}{normalized})"

    def rewrite_image(match: re.Match) -> str:
        alt, url = match.group(1), match.group(2).strip()
        if url.startswith(("http://", "https://", "data:")):
            return match.group(0)
        normalized = url.lstrip("./")
        return f"![{alt}]({raw_base}{normalized})"

    markdown = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", rewrite_link, markdown)
    markdown = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", rewrite_image, markdown)
    return markdown


def parse_markdown_sections(markdown: str) -> Dict[str, str]:
    lines = markdown.splitlines()
    sections: Dict[str, List[str]] = {}
    current = "intro"
    sections[current] = []

    for line in lines:
        heading = re.match(r"^(#{2,6})\s+(.*)$", line)
        if heading:
            current = heading.group(2).strip().lower()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)

    flattened: Dict[str, str] = {}
    for key, value in sections.items():
        text = "\n".join(value).strip()
        if text:
            flattened[key] = text
    return flattened


def bucket_section_text(sections: Dict[str, str], bucket: str) -> str:
    keywords = SECTION_BUCKETS[bucket]
    matches = []
    for heading, text in sections.items():
        if any(keyword in heading for keyword in keywords):
            snippet = text.strip()
            if snippet:
                matches.append(f"### {heading.title()}\n\n{snippet}")
    if not matches:
        return "Not available in source README."
    return "\n\n".join(matches)


def first_nonempty_paragraph(markdown: str) -> str:
    blocks = [block.strip() for block in markdown.split("\n\n")]
    for block in blocks:
        if block and not block.startswith("#"):
            return block
    return "No summary paragraph found in source README."


def workshop_page_path(workshop_id: str) -> Path:
    return WORKSHOPS_DIR / f"{workshop_id}.md"


def write_workshop_page(workshop: Dict[str, str], data: Dict[str, str]) -> None:
    path = workshop_page_path(workshop["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# {workshop['title']}

Source repository: https://github.com/{workshop['repo']}

Sync status: {data['status']}

Last synced (UTC): {data['synced_at']}

Source default branch: {data.get('branch', 'unknown')}

Source latest commit: {data.get('sha', 'unknown')}

## Summary

{data.get('summary', 'No summary available.')}

## Setup and Prerequisites

{data.get('setup', 'Not available in source README.')}

## Tasks and Exercises

{data.get('tasks', 'Not available in source README.')}

## Testing and Validation

{data.get('testing', 'Not available in source README.')}

## Troubleshooting

{data.get('troubleshooting', 'Not available in source README.')}

## References

- Source repository: https://github.com/{workshop['repo']}
- Source README: https://github.com/{workshop['repo']}/blob/{data.get('branch', 'main')}/README.md

## Imported README Snapshot

{data.get('readme', '_README unavailable due to fetch error._')}
"""
    path.write_text(content.strip() + "\n", encoding="utf-8")


def write_workshop_index(results: List[Dict[str, str]], generated_at: str) -> None:
    WORKSHOPS_DIR.mkdir(parents=True, exist_ok=True)
    rows = ["| Workshop | Repository | Status | Branch | Commit |", "|---|---|---|---|---|"]
    for item in results:
        rows.append(
            "| "
            f"[{item['title']}]({item['id']}.md)"
            " | "
            f"[{item['repo']}](https://github.com/{item['repo']})"
            " | "
            f"{item['status']}"
            " | "
            f"{item.get('branch', 'unknown')}"
            " | "
            f"{item.get('sha', 'unknown')[:12]}"
            " |"
        )

    index = f"""# Workshop Index

Generated at (UTC): {generated_at}

{chr(10).join(rows)}
"""
    (WORKSHOPS_DIR / "index.md").write_text(index, encoding="utf-8")


def build_report(results: List[Dict[str, str]], generated_at: str) -> None:
    report = {
        "generatedAt": generated_at,
        "results": results,
    }
    SYNC_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


def fetch_workshop_data(workshop: Dict[str, str], generated_at: str) -> Dict[str, str]:
    repo = workshop["repo"]
    repo_data, repo_error = github_get_json(f"/repos/{repo}")

    if repo_error or not repo_data:
        return {
            "id": workshop["id"],
            "title": workshop["title"],
            "repo": repo,
            "status": f"error ({repo_error or 'unknown'})",
            "synced_at": generated_at,
            "summary": "Repository metadata could not be fetched.",
            "readme": "_README unavailable due to repository access error._",
        }

    branch = repo_data.get("default_branch", "main")
    sha = "unknown"
    commit_data, commit_error = github_get_json(f"/repos/{repo}/commits/{branch}")
    if not commit_error and commit_data:
        sha = commit_data.get("sha", "unknown")

    readme_raw, readme_error = github_get_text(
        f"/repos/{repo}/readme", "application/vnd.github.raw+json"
    )

    if readme_error or not readme_raw:
        return {
            "id": workshop["id"],
            "title": workshop["title"],
            "repo": repo,
            "status": f"partial (README unavailable: {readme_error or 'unknown'})",
            "synced_at": generated_at,
            "branch": branch,
            "sha": sha,
            "summary": "Repository is available, but README could not be fetched.",
            "readme": "_README unavailable due to fetch error._",
        }

    normalized = normalize_links(readme_raw, repo, branch)
    sections = parse_markdown_sections(normalized)

    return {
        "id": workshop["id"],
        "title": workshop["title"],
        "repo": repo,
        "status": "ok",
        "synced_at": generated_at,
        "branch": branch,
        "sha": sha,
        "summary": first_nonempty_paragraph(normalized),
        "setup": bucket_section_text(sections, "setup"),
        "tasks": bucket_section_text(sections, "tasks"),
        "testing": bucket_section_text(sections, "testing"),
        "troubleshooting": bucket_section_text(sections, "troubleshooting"),
        "readme": normalized,
    }


def main() -> int:
    workshops = load_workshops()
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    results: List[Dict[str, str]] = []
    for workshop in workshops:
        data = fetch_workshop_data(workshop, generated_at)
        results.append(data)
        write_workshop_page(workshop, data)

    write_workshop_index(results, generated_at)
    build_report(results, generated_at)

    ok = sum(1 for item in results if item["status"] == "ok")
    errors = len(results) - ok
    print(f"Wiki sync complete. ok={ok} errors={errors}")

    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
