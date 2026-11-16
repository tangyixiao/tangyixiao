"""Generate a small linked article card from public source, with bounded inputs."""
import argparse
import base64
import importlib.util
from datetime import date, timedelta
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
import time
import urllib.error
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "assets/generated"
_SPEC = importlib.util.spec_from_file_location('render_visuals', Path(__file__).with_name('render_visuals.py'))
visuals = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(visuals)
BLOG_REPO = "tangyixiao/tangyixiao.github.io"
CARD_FILES = (
    "isometric.svg", "development.svg", "contribution-3d-light.svg",
    "contribution-3d-dark.svg", "articles.svg", "recent-languages.svg", "activity-mobile.svg",
    "isometric-mobile.svg", "contribution-3d-mobile.svg", "contribution-details.svg", "contribution-details-mobile.svg",
) + tuple(f'project-{project["slug"]}-{language}.svg' for project in visuals.PROJECTS for language in ('zh', 'en'))
COAUTHOR = "Co-authored-by: Tangyixiao <115929632+tangyixiao@users.noreply.github.com>"
COMMIT_MESSAGE = "docs: refresh generated profile cards\n\n" + COAUTHOR + "\n"


def github_json(endpoint, max_bytes=1024 * 1024):
    url = "https://api.github.com/" + endpoint
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "tangyixiao-profile-cards"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    request = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(max_bytes + 1)
            break
        except urllib.error.HTTPError as error:
            if attempt == 2 or error.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(2 ** (attempt + 1))
        except urllib.error.URLError:
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))
    if len(body) > max_bytes:
        raise ValueError("Public source exceeds response size limit")
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
    search = complete_commit_search("search/commits?" + query)
    commits = []
    for item in search["items"][:30]:
        repository = item["repository"]
        if repository.get("private"):
            raise ValueError("Unexpected non-public repository")
        full_name = repository["full_name"]
        sha = item["sha"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", full_name) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Unexpected public commit reference")
        # This endpoint includes patches even though only file counts are needed.
        # Allow a bounded larger response, then discard patch/source text promptly.
        detail = github_json("repos/" + full_name + "/commits/" + sha + "?per_page=100", max_bytes=4 * 1024 * 1024)
        commits.append({'files': [{key: file.get(key, '' if key == 'filename' else 0)
                                   for key in ('filename', 'additions', 'deletions')}
                                  for file in detail.get('files', [])]})
    return language_totals(commits), len(commits)


def complete_commit_search(endpoint):
    for attempt in range(3):
        search = github_json(endpoint)
        if not search.get("incomplete_results"):
            return search
        if attempt < 2:
            time.sleep(2 ** (attempt + 1))
    raise ValueError("Incomplete public commit search after three attempts")


def render_recent_languages(totals, commit_count):
    total = sum(lines for _, lines in totals)
    visible = totals
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


def fetch_collaboration():
    # One public-data query avoids unbounded repository scans and avatar requests.
    searches = {
        "own_issues_open": "is:issue user:tangyixiao is:public is:open",
        "own_issues_closed": "is:issue user:tangyixiao is:public is:closed",
        "own_prs_open": "is:pr user:tangyixiao is:public is:open",
        "own_prs_closed": "is:pr user:tangyixiao is:public is:closed is:unmerged",
        "own_prs_merged": "is:pr user:tangyixiao is:public is:merged",
        "user_issues_open": "is:issue author:tangyixiao is:public is:open",
        "user_issues_closed": "is:issue author:tangyixiao is:public is:closed",
        "user_prs_open": "is:pr author:tangyixiao is:public is:open",
        "user_prs_closed": "is:pr author:tangyixiao is:public is:closed is:unmerged",
        "user_prs_merged": "is:pr author:tangyixiao is:public is:merged",
    }
    query = 'query{user(login:"tangyixiao"){contributionsCollection{totalCommitContributions totalIssueContributions totalPullRequestContributions totalPullRequestReviewContributions totalRepositoryContributions commitContributionsByRepository(maxRepositories:100){repository{nameWithOwner isPrivate primaryLanguage{name color}} contributions{totalCount}} contributionCalendar{weeks{contributionDays{date contributionCount contributionLevel}}}} repositoriesContributedTo(first:20,includeUserRepositories:false,privacy:PUBLIC,contributionTypes:[COMMIT,ISSUE,PULL_REQUEST]){totalCount nodes{nameWithOwner isPrivate}}}'
    query += " ".join(key + ":search(type:ISSUE,query:" + json.dumps(value) + "){issueCount}" for key, value in searches.items()) + "}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "tangyixiao-profile-cards"}
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("The public collaboration query requires the Actions repository token")
    headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read(1024 * 1024))
    if result.get("errors"):
        raise ValueError("Public collaboration query failed")
    data = result["data"]
    repositories = data["user"]["repositoriesContributedTo"]
    if any(repo["isPrivate"] for repo in repositories["nodes"]):
        raise ValueError("Unexpected private repository in contribution card")
    calendar = [day for week in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"] for day in week["contributionDays"]]
    return repositories, {key: data[key]["issueCount"] for key in searches}, calendar, data['user']['contributionsCollection']


def fetch_public_repository_totals():
    stars = forks = 0
    for page in range(1, 11):
        repositories = github_json(f'users/tangyixiao/repos?type=owner&per_page=100&page={page}')
        for repository in repositories:
            if repository['private'] or repository['owner']['login'].lower() != 'tangyixiao':
                raise ValueError('Unexpected repository in public totals')
            stars += repository['stargazers_count']
            forks += repository['forks_count']
        if len(repositories) < 100:
            return {'stars': stars, 'forks': forks}
    raise ValueError('Public repository pagination exceeded 1000; refusing partial totals')


def fetch_projects():
    projects = []
    for project in visuals.PROJECTS:
        endpoint = 'repos/tangyixiao/' + project['slug']
        info = github_json(endpoint)
        release = github_json(endpoint + '/releases/latest') if project.get('release') else None
        projects.append((info, release))
    return projects


def github_palette(text):
    colors = {'45648a':'0969da','455467':'1f2328','759180':'0969da','d9e1e8':'d1d9e0','9db9d1':'58a6ff','c5cdd7':'e6edf3','98ad9f':'58a6ff','65758a':'59636e','a5b0bd':'9198a1','263c32':'12243a','dce6e0':'ddf4ff'}
    for before,after in colors.items():
        text = re.sub(before, after, text, flags=re.I)
    return text


def render_mobile_activity(calendar):
    days = sorted(calendar, key=lambda day: day["date"])[-14:]
    if len(days) != 14 or len({day["date"] for day in days}) != 14:
        raise ValueError("Need fourteen unique public contribution days")
    for day in days:
        date.fromisoformat(day["date"])
        if day["contributionCount"] < 0:
            raise ValueError("Negative contribution count")
    maximum = max(1, max(day["contributionCount"] for day in days))
    points = [(40 + i * 360 / 13, 197 - day["contributionCount"] * 126 / maximum) for i, day in enumerate(days)]
    line = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    area = f"40,197 {line} 400,197"
    circles = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" class="dot"/>' for x, y in points)
    labels = "".join(f'<text class="label" text-anchor="middle" x="{points[i][0]:.2f}" y="224">{days[i]["date"][5:]}</text>' for i in (0, 4, 8, 13))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="250" viewBox="0 0 420 250" role="img" aria-label="Recent fourteen days of public GitHub contributions">
<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.frame{{fill:#fff;stroke:#d9e1e8}}.heading{{fill:#45648a;font-size:18px;font-weight:600}}.label{{fill:#455467;font-size:14px}}.area{{fill:#dce6e0}}.line{{stroke:#759180;stroke-width:2.5;fill:none}}.dot{{fill:#45648a}}.axis{{stroke:#d9e1e8;fill:none}}@media(prefers-color-scheme:dark){{.frame{{fill:#0d1117;stroke:#30363d}}.heading{{fill:#9db9d1}}.label{{fill:#c5cdd7}}.area{{fill:#263c32}}.line{{stroke:#98ad9f}}.dot{{fill:#9db9d1}}.axis{{stroke:#30363d}}}}</style>
<rect class="frame" x=".5" y=".5" width="419" height="249" rx="6"/><text class="heading" x="20" y="31">Recent 14 days</text><text class="label" x="20" y="55">Contributions</text><path class="axis" d="M40 71V197H400"/><text class="label" x="32" y="83" text-anchor="end">{maximum}</text><text class="label" x="32" y="202" text-anchor="end">0</text><polygon class="area" points="{area}"/><polyline class="line" points="{line}"/>{circles}{labels}</svg>'''


def render_collaboration(repositories, counts):
    names = sorted(repo["nameWithOwner"] for repo in repositories["nodes"])[:10]
    rows = []
    for index, name in enumerate(names):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", name):
            raise ValueError("Invalid public repository handle")
        shown = name if len(name) <= 55 else name[:52] + "…"
        rows.append(f'<a href="https://github.com/{escape(name, quote=True)}"><text class="label" x="20" y="{76+index*24}">↗ {escape(shown)}</text></a>')
    if not names:
        rows.append('<text class="label" x="20" y="76">No matching public repositories</text>')
    y = 108 + max(1, len(names)) * 24
    rows.append(f'<text class="heading" x="20" y="{y}">Issues &amp; pull requests</text>')
    for prefix, title in [("own", "On my public repositories"), ("user", "Created by me · public")]:
        y += 30
        rows.append(f'<text class="label" x="20" y="{y}">{title}</text>')
        y += 25
        rows.append(f'<text class="scope" x="20" y="{y}">Issues</text><text class="label" x="454" y="{y}" text-anchor="end">{counts[prefix+"_issues_open"]} open · {counts[prefix+"_issues_closed"]} closed</text>')
        y += 25
        rows.append(f'<text class="scope" x="20" y="{y}">PRs</text><text class="label" x="454" y="{y}" text-anchor="end">{counts[prefix+"_prs_open"]} open · {counts[prefix+"_prs_merged"]} merged · {counts[prefix+"_prs_closed"]} closed</text>')
    height = y + 23
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}" viewBox="0 0 480 {height}" role="img" aria-label="Public open-source contributions and collaboration">
<style>text{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.frame{{fill:#fff;stroke:#d9e1e8}}.heading{{fill:#45648a;font-size:17px;font-weight:600}}.label{{fill:#455467;font-size:14px}}.scope{{fill:#65758a;font-size:12px}}@media(prefers-color-scheme:dark){{.frame{{fill:#0d1117;stroke:#30363d}}.heading{{fill:#9db9d1}}.label{{fill:#c5cdd7}}.scope{{fill:#a5b0bd}}}}</style>
<rect class="frame" x=".5" y=".5" width="479" height="{height-1}" rx="6"/>
<text class="heading" x="20" y="30">Open-source contributions</text><text class="scope" x="20" y="52">{repositories["totalCount"]} public repositories · last year</text>{''.join(rows)}</svg>'''


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
    repositories, counts, calendar, collection = fetch_collaboration()
    (OUTPUT / "development.svg").write_text(render_collaboration(repositories, counts), encoding="utf-8")
    (OUTPUT / "activity-mobile.svg").write_text(render_mobile_activity(calendar), encoding="utf-8")
    visuals.generate_visuals(OUTPUT, calendar, collection, fetch_public_repository_totals(), fetch_projects())
    for name in ('articles.svg', 'recent-languages.svg', 'development.svg', 'activity-mobile.svg'):
        path = OUTPUT / name
        path.write_text(github_palette(path.read_text(encoding='utf-8')), encoding='utf-8')
    if args.validate_all:
        validate_cards(OUTPUT)
    print(json.dumps({"articles": len(articles), "slugs": [item["slug"] for item in articles], "recent_commits": commit_count, "language_changes": totals, "public_collaboration": counts}))


if __name__ == "__main__":
    main()
