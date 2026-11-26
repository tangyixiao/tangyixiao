from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
README_FILES = {
    "en": ROOT / "README.md",
    "zh": ROOT / "README.zh-CN.md",
    "de": ROOT / "README.de.md",
    "fr": ROOT / "README.fr.md",
    "ru": ROOT / "README.ru.md",
}


class ProfileReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {code: path.read_text(encoding="utf-8") for code, path in README_FILES.items()}

    def test_multilingual_files_and_links(self):
        self.assertFalse((ROOT / "README.en.md").exists(), "English is now the default README.md")
        self.assertIn("Hi, I'm Yixiao Tang", self.docs["en"])
        self.assertIn("你好，我是 Yixiao Tang", self.docs["zh"])
        self.assertIn("Hallo, ich bin Yixiao Tang", self.docs["de"])
        self.assertIn("Bonjour, je suis Yixiao Tang", self.docs["fr"])
        self.assertIn("Привет, я Yixiao Tang", self.docs["ru"])

        for code, text in self.docs.items():
            for other_code, path in README_FILES.items():
                if other_code != code:
                    self.assertIn(f"({path.name})", text)

    def test_no_school_highschool_oi_or_domestic_social_links(self):
        forbidden = [
            "绍兴市第一中学",
            "Shaoxing No.1 High School",
            "Shaoxingyizhong",
            "高中生",
            "high-school student",
            "1000 AC",
            "2000 AC",
            "37662981@qq.com",
            "luogu.com.cn",
            "cnblogs.com",
            "blog.csdn.net",
            "space.bilibili.com",
            "study-desk.png",
            "csp-preview.png",
            "blackhole-preview.png",
            "drawai-preview.png",
        ]
        for code, text in self.docs.items():
            for token in forbidden:
                self.assertNotIn(token, text, f"{code} should not contain {token}")

    def test_featured_projects(self):
        urls = [
            "https://github.com/tangyixiao/HarnessHub",
            "https://github.com/tangyixiao/dsh-plugin-market",
            "https://github.com/tangyixiao/dsh-plugins-sync",
            "https://github.com/tangyixiao/dsh-workbuddy-connect-community",
            "https://github.com/tangyixiao/dsh-provider-doctor",
            "https://github.com/tangyixiao/dsh-pr-release-workspace",
            "https://github.com/tangyixiao/dsh-version-manager",
            "https://github.com/tangyixiao/dsh-zcode-plan-bridge",
            "https://github.com/tangyixiao/drawai-video-studio",
            "https://github.com/tangyixiao/tangyixiao.github.io",
            "https://github.com/tangyixiao/OJ-NEXUS",
            "https://github.com/tangyixiao/tangyixiao-workflow",
        ]
        for code, text in self.docs.items():
            for url in urls:
                self.assertIn(url, text, f"{code} missing {url}")

    def test_repository_links_match_across_languages(self):
        pattern = r"https://github\.com/tangyixiao/([A-Za-z0-9_.-]+)"
        en_repos = set(re.findall(pattern, self.docs["en"]))
        for code, text in self.docs.items():
            self.assertEqual(set(re.findall(pattern, text)), en_repos, f"repo mismatch in {code}")

    def test_local_assets_exist(self):
        for code, text in self.docs.items():
            for source in re.findall(r'src="([^"]+)"', text):
                if "://" in source:
                    continue
                asset = (ROOT / source).resolve()
                self.assertTrue(asset.is_relative_to(ROOT.resolve()))
                self.assertTrue(asset.is_file(), f"{code}: missing {source}")

    def test_cards_and_badges_preserved(self):
        for code, text in self.docs.items():
            self.assertIn("github-stats-extended.vercel.app/api?", text)
            self.assertIn("/api/top-langs/", text)
            self.assertIn("streak-stats.demolab.com", text)
            self.assertIn("github-stats-extended.vercel.app/api/pin/", text)
            self.assertIn("github-readme-activity-graph.ashutosh-dwivedi0710.workers.dev", text)
            for image in [
                "isometric.svg",
                "contribution-3d-light.svg",
                "contribution-3d-dark.svg",
                "development.svg",
                "recent-languages.svg",
            ]:
                self.assertIn("assets/generated/" + image, text)
            for label, color in {
                "C%2B%2B": "00599C",
                "TypeScript": "3178C6",
                "Python": "FFD43B",
                "Kotlin": "7F52FF",
                "Rust": "CE422B",
                "LaTeX": "008080",
            }.items():
                self.assertIn("/badge/" + label + "-" + color + "?", text)


if __name__ == "__main__":
    unittest.main()
