import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

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


if __name__ == "__main__":
    unittest.main()
