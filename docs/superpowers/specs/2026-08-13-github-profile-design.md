# GitHub Profile README Design

## Goal

Create a concise, bilingual GitHub Profile README for `tangyixiao` that acts as the entry point to a broader personal web presence.

The README should communicate four core identities within a few seconds:

- High school student at Shaoxing No.1 High School
- OI / competitive programming enthusiast
- Mathematics and physics learner
- AI / open-source explorer

Chinese and English are both first-class content languages. The README should not merely append English labels to Chinese sections; core identity, section titles, and key descriptions should be presented bilingually.

## Role in the Overall System

The GitHub Profile README is the compact public-facing card.

It should:

- introduce Tang Yixiao quickly
- highlight representative interests and projects
- surface competitive-programming progress
- link outward to the full personal website at `tangyixiao.github.io`

It should not try to reproduce the full visual and interactive website inside GitHub Markdown.

## Visual Direction

Style: student/OI personalized, clean, modern, slightly dynamic.

Principles:

- dark-mode friendly
- blue / cyan / violet technology feel where external cards or SVGs are used
- restrained badges and dynamic cards
- no school badge or school emblem
- no excessive animation
- no cluttered wall of badges
- no generic self-praise or inflated claims
- mobile-friendly GitHub Markdown layout

## Page Structure

### 1. Hero

Centered bilingual introduction:

- `唐一潇 / Tang Yixiao`
- `高中生 · OI / 信息学竞赛 · 数学与物理 · AI`
- `High School Student · Competitive Programming · Mathematics & Physics · AI`

A restrained typing-animation image may be used if it remains readable and does not dominate the page.

The main call to action should link to the personal website:

- `访问个人主页 / Visit My Website`

### 2. About / 关于我

Keep the section short and factual.

Suggested content themes:

- studying at Shaoxing No.1 High School
- learning and practicing algorithms / OI
- interested in mathematics and physics
- exploring AI, LLMs, agents, and open-source projects
- maintaining notes, code, learning resources, and templates

Both language versions should carry equivalent meaning rather than one being a partial translation.

### 3. Skills & Interests / 技术与兴趣

Use a controlled set of shields/icons for:

- C++
- Python
- LaTeX
- Markdown
- Git / GitHub
- Competitive Programming
- Mathematics
- Physics
- AI / LLM / Agent

Avoid presenting technologies from forked repositories as personal skills unless they clearly reflect current work.

### 4. Featured Projects / 精选项目

Highlight a small number of repositories that best represent the profile:

1. `Code`
   - 算法竞赛代码与学习记录
   - Competitive programming solutions and notes
2. `HighSchoolMathematics`
   - 高中数学资料与学习整理
   - High-school mathematics notes and resources
3. `Agent-Learning-Hub`
   - AI Agent 与大模型学习资料
   - Learning materials for AI agents and LLMs
4. `Shaoxing-No.1-High-School-LaTeX-Beamer-Template`
   - 绍兴一中 LaTeX Beamer 演示文稿模板
   - A LaTeX Beamer presentation template for Shaoxing No.1 High School
5. `tangyixiao.github.io`
   - 个人网站与实验性页面入口
   - Personal website and web experiments

Use text links or compact cards. Avoid listing every repository.

### 5. Competitive Programming / 信息学竞赛

Include a compact set of relevant links and progress indicators:

- Luogu
- AtCoder
- Codeforces
- GitHub code archive

Use dynamic rating cards only where the public endpoints are reliable and visually consistent.

Preserve only a few meaningful milestones, for example:

- `2026.01 — 1000 AC`
- `2026.06 — 2000 AC`

Do not copy the full historical milestone log into the profile.

### 6. GitHub Activity / GitHub 活动

Use at most two or three cards, such as:

- GitHub stats
- top languages
- contribution streak

Prefer stable public providers and a layout that remains understandable if a third-party image endpoint fails.

### 7. Find Me / 找到我

Provide a compact set of links:

- Personal website
- GitHub
- Luogu
- Blog Garden / cnblogs
- CSDN
- Bilibili

Do not expose the GitHub account email address in the README.

### 8. Footer

Use a short bilingual closing:

> 心有所向，日复一日，必有精进。
>
> Stay curious. Keep building.

## Implementation Constraints

- Implement in `README.md` using GitHub-flavored Markdown and safe inline HTML only.
- Do not depend on custom CSS or JavaScript inside the README because GitHub sanitizes unsupported markup and styles.
- Keep external image dependencies limited.
- Prefer light/dark-theme compatible cards when available.
- Avoid private information.
- Do not include a school emblem.

## Relationship to Personal Website

The README and website should share:

- the same bilingual identity statement
- the same project selection
- the same blue/cyan/violet visual tone
- the same major external links

The README should deliberately remain lighter and more maintainable than the website.

## Success Criteria

A visitor should understand within a few seconds that Tang Yixiao is a high-school student focused on OI/algorithms, mathematics, physics, and AI.

The profile should look polished and personal, use Chinese and English equally for core content, and strongly direct interested visitors toward the full personal website without becoming a badge-heavy template.
