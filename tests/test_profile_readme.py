from pathlib import Path
import unittest

README = Path(__file__).resolve().parents[1] / "README.md"

class ProfileReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = README.read_text(encoding="utf-8")

    def test_bilingual_identity(self):
        for token in [
            "唐一潇 / Tang Yixiao",
            "高中生 · OI / 信息学竞赛 · 数学与物理 · AI",
            "High School Student · Competitive Programming · Mathematics & Physics · AI",
        ]:
            self.assertIn(token, self.text)

    def test_required_sections(self):
        for heading in [
            "关于我 / About Me",
            "技术与兴趣 / Skills & Interests",
            "精选项目 / Featured Projects",
            "信息学竞赛 / Competitive Programming",
            "GitHub 活动 / GitHub Activity",
            "找到我 / Find Me",
        ]:
            self.assertIn(heading, self.text)

    def test_primary_website_link(self):
        self.assertIn("https://tangyixiao.github.io/", self.text)

    def test_featured_projects(self):
        for url in [
            "https://github.com/tangyixiao/Code",
            "https://github.com/tangyixiao/HighSchoolMathematics",
            "https://github.com/tangyixiao/Agent-Learning-Hub",
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

    def test_private_email_not_exposed(self):
        self.assertNotIn("37662981@qq.com", self.text)

if __name__ == "__main__":
    unittest.main()
