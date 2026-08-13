# GitHub Profile README Design

## Goal

Create a personal GitHub Profile README for `tangyixiao` that feels recognizably personal rather than like a generic developer template.

The page should present four core identities clearly:

- High school student at Shaoxing No.1 High School
- OI / competitive programming enthusiast
- Mathematics and physics learner
- AI / open-source explorer

The design should be bilingual where useful, with Chinese as the primary language and concise English labels for international readability.

## Visual Direction

Style: student/OI personalized, clean, modern, slightly dynamic.

Principles:

- Dark-mode friendly
- Blue / cyan / violet technology feel
- Moderate use of badges and dynamic cards
- No school badge or school emblem
- No excessive animation
- No cluttered wall of badges
- No generic self-praise or inflated claims
- Mobile-friendly GitHub Markdown layout

## Page Structure

### 1. Hero

Centered introduction:

- `Hi, I'm 唐一潇 / Tang Yixiao 👋`
- Short identity line such as:
  - `High School Student · OI / Competitive Programming · Mathematics · AI`
- A restrained typing-animation line may be used for rotating interests.

The hero should immediately communicate who the profile belongs to without taking too much vertical space.

### 2. About Me

Short bilingual introduction focused on current interests:

- Student at Shaoxing No.1 High School
- Learning and practicing algorithms / OI
- Interested in mathematics and physics
- Exploring AI, LLMs, agents, and open-source projects
- Building notes, tools, templates, and code repositories

Keep this section compact and factual.

### 3. Skills & Interests

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

Avoid presenting every technology encountered in forked repositories as a personal skill.

### 4. Featured Projects

Highlight a small number of repositories that best represent the profile:

1. `Code`
   - OI / competitive programming code and learning archive
2. `HighSchoolMathematics`
   - High school mathematics materials and notes
3. `Agent-Learning-Hub`
   - AI / agent learning materials
4. `Shaoxing-No.1-High-School-LaTeX-Beamer-Template`
   - A LaTeX Beamer presentation template for Shaoxing No.1 High School
5. `tangyixiao.github.io`
   - Personal website / web experiments

Use text links or compact repository cards. Avoid listing all repositories.

### 5. Competitive Programming

Include links and dynamic rating images already associated with the user where reliable:

- Luogu profile / blog
- AtCoder rating card
- Codeforces rating card

Preserve only a few meaningful milestones rather than the full historical list. Suggested milestones:

- `2026.01 — 1000 AC`
- `2026.06 — 2000 AC`

This section should feel like a record of progress, not a leaderboard wall.

### 6. GitHub Activity

Use at most two or three dynamic widgets/cards, for example:

- GitHub stats
- Top languages
- Contribution streak

Prefer services with stable public endpoints. The layout should degrade gracefully if a third-party card provider is unavailable.

### 7. Find Me

Provide a compact set of personal links:

- GitHub
- Personal website
- Luogu
- Blog Garden / cnblogs
- CSDN
- Bilibili

Do not expose the GitHub account email address in the README.

### 8. Footer

Use a short personal closing line:

> 心有所向，日复一日，必有精进。

And optionally:

> Stay curious. Keep building.

No large decorative footer image is required.

## Content Sources

The implementation may reuse useful links from the existing `Code/README.md`, but should not copy its long quote collection or full milestone log into the profile.

The current profile README is still the default GitHub template and can be replaced entirely.

## Technical Constraints

- Implement entirely in `README.md` using GitHub-flavored Markdown and safe inline HTML where needed.
- Do not require JavaScript.
- Keep external image dependencies limited.
- Use URLs that work in both GitHub light and dark themes when possible.
- Keep image widths responsive and avoid layouts that break on mobile.
- Avoid private information.
- Do not include a school emblem.

## Success Criteria

The finished profile should let a visitor understand within a few seconds that Tang Yixiao is a high-school student focused on OI/algorithms, mathematics, and AI.

It should look polished and personal, but remain readable, maintainable, and noticeably less cluttered than common badge-heavy GitHub profile templates.
