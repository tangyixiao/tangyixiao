import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cards", ROOT / "scripts/profile-cards/generate_articles.py")
cards = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cards)


class ProfileCardGeneratorTests(unittest.TestCase):
    def test_article_metadata_preserves_real_date_and_link(self):
        article = cards.parse_article("---\ntitle: A & B <test>\ndate: 2026-10-02\nslug: agent-experiment\n---\nBody")
        svg = cards.render_articles([article])
        root = ET.fromstring(svg)
        self.assertIn("A & B <test>", "".join(root.itertext()))
        self.assertIn("2026-10-02", "".join(root.itertext()))
        self.assertIn('href="https://tangyixiao.github.io/blog/posts/agent-experiment.html"', svg)

    def test_bad_metadata_cannot_create_a_fake_link_or_date(self):
        for date, slug in [("2026-02-30", "good"), ("2026-01-01", "../bad"), ("2026-01-01", 'bad" onclick="x')]:
            with self.assertRaises(ValueError):
                cards.parse_article(f"---\ntitle: Test\ndate: {date}\nslug: {slug}\n---\n")

    def test_publication_rejects_incomplete_or_active_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            with self.assertRaises(ValueError):
                cards.validate_cards(directory)
            for name in cards.CARD_FILES:
                (directory / name).write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
            cards.validate_cards(directory)
            (directory / "articles.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>', encoding="utf-8")
            with self.assertRaises(ValueError):
                cards.validate_cards(directory)

    def test_every_bot_commit_uses_recognized_joint_credit(self):
        result = subprocess.run(["git", "interpret-trailers", "--parse"], input=cards.COMMIT_MESSAGE, text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout.strip(), cards.COAUTHOR)
        workflow = (ROOT / ".github/workflows/profile-cards.yml").read_text(encoding="utf-8")
        self.assertIn("--commit-message work/profile-card-commit.txt", workflow)
        self.assertIn("git commit --file work/profile-card-commit.txt", workflow)
        self.assertNotIn("secrets.METRICS_TOKEN", workflow)

    def test_recent_languages_count_changes_and_exclude_generator_outputs(self):
        totals = cards.language_totals([{"files": [
            {"filename": "src/a.ts", "additions": 4, "deletions": 3},
            {"filename": "src/b.tsx", "additions": 2, "deletions": 0},
            {"filename": "main.py", "additions": 5, "deletions": 1},
            {"filename": "assets/generated/a.svg", "additions": 1000, "deletions": 0},
            {"filename": "README.md", "additions": 500, "deletions": 0},
        ]}])
        self.assertEqual(totals, [("TypeScript", 9), ("Python", 6)])
        root = ET.fromstring(cards.render_recent_languages(totals, 1))
        text = "".join(root.itertext())
        self.assertIn("60.0%", text)
        self.assertIn("40.0%", text)
        self.assertIn("1 public commits sampled", text)

    def test_collaboration_labels_do_not_merge_owner_and_author_scopes(self):
        counts = {prefix + "_" + key: number for prefix in ("own", "user") for key, number in {"issues_open": 1, "issues_closed": 2, "prs_open": 3, "prs_closed": 4, "prs_merged": 5}.items()}
        svg = cards.render_collaboration({"totalCount": 1, "nodes": [{"nameWithOwner": "public/repo"}]}, counts)
        root = ET.fromstring(svg)
        text = "".join(root.itertext())
        self.assertIn("On my public repositories", text)
        self.assertIn("Created by me", text)
        self.assertIn("3 open · 5 merged · 4 closed", text)
        with self.assertRaises(ValueError):
            cards.render_collaboration({"totalCount": 1, "nodes": [{"nameWithOwner": 'bad/"path'}]}, counts)

    def test_mobile_activity_uses_real_fourteen_day_range_and_handles_zeroes(self):
        days = [{"date": (date(2026, 11, 1) + timedelta(days=i)).isoformat(), "contributionCount": 0} for i in range(20)]
        svg = cards.render_mobile_activity(days)
        root = ET.fromstring(svg)
        text = "".join(root.itertext())
        self.assertIn("11-07", text)
        self.assertIn("11-20", text)
        self.assertNotIn("NaN", svg)
        with self.assertRaises(ValueError):
            cards.render_mobile_activity(days[:5])

    def test_incomplete_search_is_retried_but_never_published(self):
        complete = {"incomplete_results": False, "items": []}
        incomplete = {"incomplete_results": True, "items": []}
        with patch.object(cards, "github_json", side_effect=[incomplete, complete]) as query, patch.object(cards.time, "sleep"):
            self.assertEqual(cards.complete_commit_search("search/commits?q=test"), complete)
            self.assertEqual(query.call_count, 2)
        with patch.object(cards, "github_json", return_value=incomplete) as query, patch.object(cards.time, "sleep"):
            with self.assertRaises(ValueError):
                cards.complete_commit_search("search/commits?q=test")
            self.assertEqual(query.call_count, 3)

    def test_calendar_preserves_every_real_date_and_rejects_gaps(self):
        days = [{'date': (date(2025, 11, 20)+timedelta(days=i)).isoformat(),
                 'contributionCount': 0, 'contributionLevel': 'NONE'} for i in range(365)]
        for landscape in (False, True):
            for mobile in (False, True):
                source = cards.visuals.render_calendar(days, landscape=landscape, mobile=mobile, stats={'stars': 0, 'forks': 0})
                root = ET.fromstring(source)
                titles = root.findall('.//{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}title')
                self.assertEqual(len(titles), 365)
                self.assertIn('2025-11-20: 0 contributions', [t.text for t in titles])
                self.assertNotIn('NaN', source)
                if not landscape:
                    self.assertIn('Highest in a day 0', source)
        with self.assertRaises(ValueError):
            cards.visuals.calendar_days(days[:100]+days[101:])
        with self.assertRaises(ValueError):
            cards.visuals.calendar_days(days[:-1]+[days[-2]])

    def test_language_chart_keeps_all_named_languages_without_other(self):
        entries = [{'repository': {'isPrivate': False, 'primaryLanguage': {'name': name, 'color': '#123456'}},
                    'contributions': {'totalCount': i+1}} for i,name in enumerate(['HTML','Kotlin','TypeScript','Rust','JavaScript','C++','Python','CSS','Shell'])]
        collection = {'commitContributionsByRepository': entries, **{k: 0 for k in ('totalCommitContributions','totalIssueContributions','totalPullRequestContributions','totalPullRequestReviewContributions','totalRepositoryContributions')}}
        for mobile in (False, True):
            source = cards.visuals.render_details(collection, mobile)
            labels = ''.join(ET.fromstring(source).itertext())
            for entry in entries:
                self.assertIn(entry['repository']['primaryLanguage']['name'], labels)
            self.assertNotIn('other', labels.lower())
        entries[0]['repository']['isPrivate'] = True
        with self.assertRaises(ValueError):
            cards.visuals.language_contributions(entries)

    def test_public_totals_paginate_instead_of_truncating_at_one_page(self):
        repo = {'private':False,'owner':{'login':'tangyixiao'},'stargazers_count':1,'forks_count':2}
        with patch.object(cards, 'github_json', side_effect=[[repo]*100, [repo]*7]) as query:
            self.assertEqual(cards.fetch_public_repository_totals(), {'stars':107,'forks':214})
            self.assertEqual(query.call_count, 2)
        with patch.object(cards, 'github_json', return_value=[repo]*100):
            with self.assertRaises(ValueError):
                cards.fetch_public_repository_totals()


if __name__ == "__main__":
    unittest.main()
