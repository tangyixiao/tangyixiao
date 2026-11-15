from pathlib import Path
import re
import unittest

README = Path(__file__).resolve().parents[1] / "README.md"

class ProfileReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")
        cls.english = README.with_name("README.en.md").read_text(encoding="utf-8")

    def test_bilingual_identity(self):
        for token in ["唐一潇", "绍兴市第一中学", "高中生", "数学和物理"]:
            self.assertIn(token, self.text)
        for token in ["Tang Yixiao", "Shaoxing No.1 High School", "high-school student"]:
            self.assertIn(token, self.english)
        self.assertIn("[English](README.en.md)", self.text)
        self.assertIn("[简体中文](README.md)", self.english)

    def test_required_sections(self):
        for heading in [
            "最近的几个进展",
            "信息学与学习",
            "AI 编程工具与社区插件",
            "网站、可视化与表达",
            "写过的一些东西",
            "项目里用到的技术",
            "在其他地方找到我",
        ]:
            self.assertIn(heading, self.text)

    def test_primary_website_link(self):
        self.assertIn("https://tangyixiao.github.io/", self.text)

    def test_featured_projects(self):
        for url in [
            "https://github.com/tangyixiao/CSP-2026",
            "https://github.com/tangyixiao/OJ-NEXUS",
            "https://github.com/tangyixiao/oi-coach",
            "https://github.com/tangyixiao/evidence-learning",
            "https://github.com/tangyixiao/dsh-workbuddy-connect-community",
            "https://github.com/tangyixiao/dsh-pr-release-workspace",
            "https://github.com/tangyixiao/dsh-plugin-market",
            "https://github.com/tangyixiao/HarnessHub",
            "https://github.com/tangyixiao/drawai-video-studio",
            "https://github.com/tangyixiao/tangyixiao.github.io",
            "https://github.com/tangyixiao/Shaoxing-No.1-High-School-LaTeX-Beamer-Template",
        ]:
            self.assertIn(url, self.text)

    def test_public_links(self):
        for url in [
            "https://www.luogu.com.cn/blog/TangyixiaoQAQ/",
            "https://home.cnblogs.com/u/TangyixiaoQAQ",
            "https://blog.csdn.net/DCMyyds",
            "https://space.bilibili.com/512272131",
            "https://github.com/tangyixiao",
        ]:
            self.assertIn(url, self.text)

    def test_selected_milestones(self):
        for token in ["2026.01", "1000 AC", "2026.06", "2000 AC"]:
            self.assertIn(token, self.text)

    def test_unavailable_repository_links_removed(self):
        for url in [
            "https://github.com/tangyixiao/Code",
            "https://github.com/tangyixiao/HighSchoolMathematics",
            "https://github.com/tangyixiao/Agent-Learning-Hub",
        ]:
            self.assertNotIn(url, self.text)

    def test_private_email_not_exposed(self):
        self.assertNotIn("37662981@qq.com", self.text)
        self.assertNotIn("37662981@qq.com", self.english)

    def test_local_images_exist(self):
        for document in [self.text, self.english]:
            for source in re.findall(r'src="([^"]+)"', document):
                if "://" in source:
                    continue
                asset = (README.parent / source).resolve()
                self.assertTrue(asset.is_relative_to(README.parent.resolve()))
                self.assertTrue(asset.is_file(), source)

    def test_repository_links_match_between_languages(self):
        pattern = r"https://github\.com/tangyixiao/([A-Za-z0-9_.-]+)"
        self.assertEqual(set(re.findall(pattern, self.text)),
                         set(re.findall(pattern, self.english)))

    def test_github_cards_and_project_previews(self):
        for document in [self.text, self.english]:
            self.assertIn("github-stats-extended.vercel.app/api?", document)
            self.assertIn("/api/top-langs/", document)
            self.assertIn("streak-stats.demolab.com", document)
            for image in ["csp-preview.png", "blackhole-preview.png", "drawai-preview.png"]:
                self.assertIn("assets/" + image, document)

if __name__ == "__main__":
    unittest.main()
