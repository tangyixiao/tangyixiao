"""Generate a small linked article card from public source, with bounded inputs."""
import argparse
import base64
from datetime import date, timedelta
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "assets/generated"
BLOG_REPO = "tangyixiao/tangyixiao.github.io"
CARD_FILES = (
    "isometric.svg", "development.svg", "contribution-3d-light.svg",
    "contribution-3d-dark.svg", "articles.svg", "recent-languages.svg",
)
COAUTHOR = "Co-authored-by: Tangyixiao <115929632+tangyixiao@users.noreply.github.com>"
COMMIT_MESSAGE = "docs: refresh generated profile cards\n\n" + COAUTHOR + "\n"


def github_json(endpoint):
    url = "https://api.github.com/" + endpoint
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "tangyixiao-profile-cards"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read(1024 * 1024 + 1)
    if len(body) > 1024 * 1024:
        raise ValueError("Public source exceeds 1 MiB limit")
    return json.loads(body)


def parse_article(text):
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not frontmatter:
        raise ValueError("Missing article metadata")
    fields = {}
    for key in ("title", "date", "slug"):
        match = re.search(r"^" + key + r":\s*([^\r\n]+)$", frontmatter.group(1), re.M)
        if not match:
            raise ValueError("Missing article " + key)
        fields[key] = match.group(1).strip().strip("\"'")
    date.fromisoformat(fields["date"])
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["slug"]):
        raise ValueError("Invalid public article slug")
    if not 1 <= len(fields["title"]) <= 100:
        raise ValueError("Invalid article title")
    fields["url"] = "https://tangyixiao.github.io/blog/posts/" + fields["slug"] + ".html"
    return fields


def fetch_articles():
    listing = github_json("repos/" + BLOG_REPO + "/contents/blog-src?ref=main")
    files = sorted(item["path"] for item in listing if item["type"] == "file" and item["name"].endswith(".md"))
    if not files or len(files) > 50:
        raise ValueError("Unexpected article collection size")
    articles = []
    for path in files:
        if not re.fullmatch(r"blog-src/[a-z0-9-]+\.md", path):
            raise ValueError("Unexpected article path")
        item = github_json("repos/" + BLOG_REPO + "/contents/" + path + "?ref=main")
        if item.get("encoding") != "base64" or item.get("size", 0) > 256 * 1024:
            raise ValueError("Unexpected public article encoding or size")
        articles.append(parse_article(base64.b64decode(item["content"]).decode("utf-8")))
    return sorted(articles, key=lambda item: (item["date"], item["slug"]), reverse=True)[:4]


def render_articles(articles):
    if not articles:
        raise ValueError("Cannot render an empty article card")
    height = 66 + 57 * len(articles)
    rows = []
    for index, article in enumerate(articles):
        y = 74 + index * 57
        rows.append(f'<a href="{escape(article["url"], quote=True)}"><text class="title" x="20" y="{y}">{escape(article["title"])}</text><text class="date" x="20" y="{y+20}">{article["date"]}</text></a>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" viewBox="0 0 480 {height}" role="img" aria-label="Recent articles">
<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}}.frame{{fill:#fff;stroke:#d9e1e8}}.heading{{fill:#45648a;font-size:17px;font-weight:600}}.title{{fill:#455467;font-size:15px}}.date{{fill:#65758a;font-size:12px}}@media(prefers-color-scheme:dark){{.frame{{fill:#0d1117;stroke:#30363d}}.heading{{fill:#9db9d1}}.title{{fill:#c5cdd7}}.date{{fill:#a5b0bd}}}}</style>
<rect class="frame" x=".5" y=".5" width="479" height="{height-1}" rx="6"/>
<text class="heading" x="20" y="30">Recent articles</text>{''.join(rows)}</svg>'''


LANGUAGES = {
    ".py": ("Python", "#3572a5"), ".ts": ("TypeScript", "#3178c6"),
    ".tsx": ("TypeScript", "#3178c6"), ".js": ("JavaScript", "#b39a30"),
    ".mjs": ("JavaScript", "#b39a30"), ".jsx": ("JavaScript", "#b39a30"),
    ".cpp": ("C++", "#d85d8d"), ".cc": ("C++", "#d85d8d"),
    ".cxx": ("C++", "#d85d8d"), ".hpp": ("C++", "#d85d8d"),
    ".c": ("C", "#555555"), ".h": ("C", "#555555"),
    ".rs": ("Rust", "#a97657"), ".kt": ("Kotlin", "#9761db"),
    ".kts": ("Kotlin", "#9761db"), ".java": ("Java", "#b07219"),
    ".html": ("HTML", "#df623e"), ".css": ("CSS", "#7350ae"),
    ".scss": ("SCSS", "#c6538c"), ".vue": ("Vue", "#41b883"),
    ".sh": ("Shell", "#759180"), ".ps1": ("PowerShell", "#407ca0"),
    ".go": ("Go", "#00add8"), ".rb": ("Ruby", "#b14236"),
    ".tex": ("TeX", "#3d7651"), ".php": ("PHP", "#6e79ae"),
}


def language_totals(commits):
    totals = {}
    for commit in commits:
        for item in commit.get("files", []):
            filename = item.get("filename", "")
            # Do not count the profile generator's own SVG output as coding activity.
            if filename.startswith(("assets/generated/", "profile-3d-contrib/")):
                continue
            language = LANGUAGES.get(Path(filename).suffix.lower())
            if not language:
                continue
            changed = int(item.get("additions", 0)) + int(item.get("deletions", 0))
            if changed < 0:
                raise ValueError("Negative change count")
            totals[language[0]] = totals.get(language[0], 0) + changed
    return sorted(((name, lines) for name, lines in totals.items() if lines), key=lambda item: (-item[1], item[0]))


def fetch_recent_languages():
    since = (date.today() - timedelta(days=14)).isoformat()
    query = urllib.parse.urlencode({"q": "author:tangyixiao is:public committer-date:>=" + since,
                                   "sort": "committer-date", "order": "desc", "per_page": 30})
    search = github_json("search/commits?" + query)
    if search.get("incomplete_results"):
        raise ValueError("Incomplete public commit search")
    commits = []
    for item in search["items"][:30]:
        repository = item["repository"]
        if repository.get("private"):
            raise ValueError("Unexpected non-public repository")
        full_name = repository["full_name"]
        sha = item["sha"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", full_name) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Unexpected public commit reference")
        commits.append(github_json("repos/" + full_name + "/commits/" + sha + "?per_page=100"))
    return language_totals(commits), len(commits)


def render_recent_languages(totals, commit_count):
    total = sum(lines for _, lines in totals)
    visible = totals[:8]
    height = 95 + max(1, len(visible)) * 31
    colors = {name: color for name, color in LANGUAGES.values()}
    rows = []
    for index, (name, lines) in enumerate(visible):
        y = 94 + index * 31
        width = 230 * lines / total
        rows.append(f'<text class="label" x="20" y="{y}">{escape(name)}</text><rect x="135" y="{y-11}" width="{width:.2f}" height="12" rx="3" fill="{colors[name]}"/><text class="label" x="454" y="{y}" text-anchor="end">{lines / total:.1%}</text>')
    if not visible:
        rows.append('<text class="label" x="20" y="94">No matching public code changes in this sample</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" viewBox="0 0 480 {height}" role="img" aria-label="Recent public code changes">
<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.frame{{fill:#fff;stroke:#d9e1e8}}.heading{{fill:#45648a;font-size:17px;font-weight:600}}.label{{fill:#455467;font-size:14px}}.scope{{fill:#65758a;font-size:12px}}@media(prefers-color-scheme:dark){{.frame{{fill:#0d1117;stroke:#30363d}}.heading{{fill:#9db9d1}}.label{{fill:#c5cdd7}}.scope{{fill:#a5b0bd}}}}</style>
<rect class="frame" x=".5" y=".5" width="479" height="{height-1}" rx="6"/>
<text class="heading" x="20" y="30">Recent languages</text><text class="scope" x="20" y="53">Changed lines · last 14 days · {commit_count} public commits sampled</text>{''.join(rows)}</svg>'''


def validate_cards(directory):
    for name in CARD_FILES:
        path = directory / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Missing, linked, or oversized card: " + name)
        text = path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
        if root.tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("Not an SVG card: " + name)
        if re.search(r"<script\b|\bonload\s*=|\bonerror\s*=|<!DOCTYPE", text, re.I):
            raise ValueError("Unexpected active SVG content: " + name)
        if "Plugin error" in text or "Could not render metrics" in text:
            raise ValueError("Upstream rendered an error: " + name)


def publish_cards(source):
    source = source.resolve()
    validate_cards(source)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name in CARD_FILES:
        shutil.copyfile(source / name, OUTPUT / name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-all", action="store_true")
    parser.add_argument("--publish-from", type=Path)
    parser.add_argument("--commit-message", type=Path)
    args = parser.parse_args()
    if args.commit_message:
        args.commit_message.parent.mkdir(parents=True, exist_ok=True)
        args.commit_message.write_text(COMMIT_MESSAGE, encoding="utf-8")
        return
    if args.publish_from:
        publish_cards(args.publish_from)
        return
    articles = fetch_articles()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "articles.svg").write_text(render_articles(articles), encoding="utf-8")
    totals, commit_count = fetch_recent_languages()
    (OUTPUT / "recent-languages.svg").write_text(render_recent_languages(totals, commit_count), encoding="utf-8")
    if args.validate_all:
        validate_cards(OUTPUT)
    print(json.dumps({"articles": len(articles), "slugs": [item["slug"] for item in articles], "recent_commits": commit_count, "language_changes": totals}))


if __name__ == "__main__":
    main()
