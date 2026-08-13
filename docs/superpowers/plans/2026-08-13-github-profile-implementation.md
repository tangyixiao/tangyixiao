# GitHub Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the default GitHub Profile README with a polished bilingual profile that introduces Tang Yixiao, highlights OI/mathematics/AI interests, surfaces representative projects and links, and directs visitors to the full personal website.

**Architecture:** Keep the Profile README self-contained in `README.md` using GitHub-flavored Markdown plus safe inline HTML. Use only a small number of external badges/cards, keep all critical information as text, and make the personal website the main outbound call to action.

**Tech Stack:** GitHub Flavored Markdown, safe inline HTML, shields.io-compatible badges, optional public stats/rating image endpoints.

## Global Constraints

- Chinese and English are both first-class for the core identity, section titles, and key descriptions.
- Do not depend on custom CSS or JavaScript inside the README.
- Do not include a school emblem.
- Do not expose the GitHub account email address.
- Keep external image dependencies limited and non-critical.
- Prefer a dark-mode-friendly blue/cyan/violet visual tone.
- Keep the page mobile-friendly and noticeably less cluttered than badge-heavy profile templates.

---

## File Structure

- Modify: `README.md` — complete Profile README.
- Create: `tests/test_profile_readme.py` — lightweight structural regression checks using only Python standard library.

### Task 1: Establish README structure and bilingual identity

**Files:**
- Modify: `README.md`
- Create: `tests/test_profile_readme.py`

**Interfaces:**
- Consumes: the approved profile design spec.
- Produces: required section headings and primary website CTA used by later tasks.

- [ ] **Step 1: Write structural tests**

Create `tests/test_profile_readme.py` with checks that `README.md` contains all required bilingual section labels, the name `唐一潇 / Tang Yixiao`, the identity lines, and the website URL `https://tangyixiao.github.io/`.

```python
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

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify the current default README fails**

Run:

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: failures for missing bilingual identity, sections, and website link.

- [ ] **Step 3: Replace the default README with the core skeleton**

Implement the Hero plus empty-but-valid section shells using headings exactly matching the test strings. The Hero must include:

```markdown
<div align="center">

# 唐一潇 / Tang Yixiao

高中生 · OI / 信息学竞赛 · 数学与物理 · AI  
High School Student · Competitive Programming · Mathematics & Physics · AI

[**访问个人主页 / Visit My Website →**](https://tangyixiao.github.io/)

</div>
```

Then add the required bilingual section headings in the order defined by the spec.

- [ ] **Step 4: Run structural tests**

Run:

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_profile_readme.py
git commit -m "feat: build bilingual profile readme structure"
```

### Task 2: Add personal content, skills, and featured projects

**Files:**
- Modify: `README.md`
- Modify: `tests/test_profile_readme.py`

**Interfaces:**
- Consumes: section structure from Task 1.
- Produces: complete bilingual copy, skill badges, and representative project links.

- [ ] **Step 1: Extend tests for representative projects and privacy**

Add checks for these repository URLs:

```python
    def test_featured_projects(self):
        for url in [
            "https://github.com/tangyixiao/Code",
            "https://github.com/tangyixiao/HighSchoolMathematics",
            "https://github.com/tangyixiao/Agent-Learning-Hub",
            "https://github.com/tangyixiao/Shaoxing-No.1-High-School-LaTeX-Beamer-Template",
        ]:
            self.assertIn(url, self.text)

    def test_private_email_not_exposed(self):
        self.assertNotIn("37662981@qq.com", self.text)
```

- [ ] **Step 2: Run tests and verify project checks fail**

Run:

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: project test fails; privacy test passes.

- [ ] **Step 3: Implement About, Skills, and Featured Projects**

Write concise equivalent Chinese/English copy covering:

- studying at Shaoxing No.1 High School
- OI / algorithms
- mathematics and physics
- AI / LLM / agents / open source
- notes, code, resources, and templates

Add a controlled badge row for `C++`, `Python`, `LaTeX`, `Markdown`, `Git`, and `AI / LLM`, without claiming technologies solely because they appear in forked repositories.

Add project entries for `Code`, `HighSchoolMathematics`, `Agent-Learning-Hub`, and `Shaoxing-No.1-High-School-LaTeX-Beamer-Template`, each with one Chinese and one English description line.

- [ ] **Step 4: Run tests**

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_profile_readme.py
git commit -m "feat: add bilingual profile content and projects"
```

### Task 3: Add competitive-programming, activity, and social links

**Files:**
- Modify: `README.md`
- Modify: `tests/test_profile_readme.py`

**Interfaces:**
- Consumes: completed content sections from Task 2.
- Produces: OI progress, rating links/cards, GitHub activity cards, and contact links.

- [ ] **Step 1: Add link regression tests**

Add checks for known public links already present in the user's repositories:

```python
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
        self.assertIn("2026.01", self.text)
        self.assertIn("1000 AC", self.text)
        self.assertIn("2026.06", self.text)
        self.assertIn("2000 AC", self.text)
```

- [ ] **Step 2: Run tests and verify the new checks fail**

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: failures for missing public links and milestones.

- [ ] **Step 3: Implement competitive-programming and activity sections**

Include text links for Luogu, AtCoder, Codeforces, and the `Code` repository. Add the two selected milestones:

```text
2026.01 — 1000 AC
2026.06 — 2000 AC
```

Optionally embed the existing AtCoder and Codeforces rating-card endpoints as progressive enhancement. Add at most two GitHub activity cards so the profile does not become visually dense.

Add Find Me links for website, GitHub, Luogu, cnblogs, CSDN, and Bilibili.

- [ ] **Step 4: Run tests**

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_profile_readme.py
git commit -m "feat: add competitive programming and profile links"
```

### Task 4: Final profile polish and verification

**Files:**
- Modify: `README.md`
- Modify: `tests/test_profile_readme.py` only if a regression check is needed.

**Interfaces:**
- Consumes: complete README.
- Produces: final deployable GitHub Profile README.

- [ ] **Step 1: Add footer and consistency pass**

Ensure the README ends with:

```markdown
> 心有所向，日复一日，必有精进。  
> Stay curious. Keep building.
```

Confirm every core descriptive section has equivalent Chinese and English meaning, and remove duplicated badges or redundant cards.

- [ ] **Step 2: Run regression tests**

```bash
python -m unittest tests/test_profile_readme.py -v
```

Expected: PASS.

- [ ] **Step 3: Validate Markdown/link hygiene**

Run:

```bash
python - <<'PY'
from pathlib import Path
p = Path('README.md')
s = p.read_text(encoding='utf-8')
assert s.count('37662981@qq.com') == 0
assert s.count('https://tangyixiao.github.io/') >= 1
assert len(s) < 20000
print('README sanity checks passed')
PY
```

Expected: `README sanity checks passed`.

- [ ] **Step 4: Review in GitHub rendering**

Open the repository root and confirm:

- Hero is centered and readable in light and dark themes.
- Project links are not broken.
- External cards, if any, are secondary to textual content.
- No horizontal overflow or excessive badge wrapping on narrow screens.

- [ ] **Step 5: Commit any final polish**

```bash
git add README.md tests/test_profile_readme.py
git commit -m "polish: finalize GitHub profile readme"
```
