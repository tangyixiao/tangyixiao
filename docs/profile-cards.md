# Profile card generation

The public profile embeds live project/version cards and contribution graphs, plus SVGs generated in this repository. The profile itself has no service footnotes.

## Generated images

`.github/workflows/profile-cards.yml` runs daily at 22:17 UTC (06:17 Asia/Shanghai), on generator changes, and on manual dispatch. The generation job has read-only repository permission; only the separate `main` publishing job can write generated images.

| File | Source and scope |
| --- | --- |
| `assets/generated/isometric{,-mobile}.svg` | The public GraphQL contribution calendar for a full year, with explicit dates, counts and GitHub contribution levels. A native renderer lays out the whole year horizontally; mobile splits the same dates into two panels. Heights are linear in daily contribution counts. The current streak allows today to be unfinished. |
| `assets/generated/development.svg` | One public GraphQL query: up to 20 external repositories contributed to in the past year (COMMIT, ISSUE, PULL_REQUEST; up to ten names displayed), plus issue and PR states in two explicitly labeled scopes: public repositories owned by the user, and public items authored by the user. Open, closed-unmerged and merged PR counts are disjoint. |
| `assets/generated/recent-languages.svg` | Changed lines (additions + deletions) in recognized code/markup files from up to 30 public commit-search results in the last 14 days, up to 100 files per commit. Every recognized language in the sample is shown by name; percentages use the full recognized sample as denominator. Generated profile images and prose/data/config extensions are excluded. This bounded activity sample is not total authored code, proficiency or time. |
| `assets/generated/contribution-3d-{light,dark,mobile}.svg` | The same public daily calendar, rendered from a front-facing view with logarithmic column heights adapted from github-profile-3d-contrib. Light/dark images have explicit palettes; the mobile image follows the theme. Stars/Forks sum all pages of owned public repositories, including forks, with a 1000-repository bound. Hitting that bound fails instead of publishing partial totals. |
| `assets/generated/contribution-details{,-mobile}.svg` | Separate language donut and contribution-type radar. All named languages returned by public `commitContributionsByRepository(maxRepositories:100)` are displayed individually; the donut denominator is the sum of contributions to repositories with a known primary language in that bounded query. Repositories without a primary language are excluded, never renamed or allocated to another language. There is no `other` bucket or top-five cut. Radar values are the five public contribution totals from the same collection; the radial scale is logarithmic. |
| `assets/generated/articles.svg` | Up to four real posts, ordered by frontmatter date and slug, from the public `blog-src` directory of `tangyixiao/tangyixiao.github.io`. Dates and titles are not inferred from Git commit timestamps. |
| `assets/generated/activity-mobile.svg` | Fourteen daily counts from the public contribution calendar, rendered at a native 420px width so mobile axis labels remain readable. |
| `assets/generated/project-*-{zh,en}.svg` | Fourteen explicitly selected public repositories. Reviewed bilingual descriptions live in `scripts/profile-cards/projects.json`; language and Stars come from current public repository metadata. Four release cards also use the latest published release's real tag and publication date. |

The lower project cards use the same 390×150 geometry, 18px repository heading, 13px description, 12px language/Stars row and blue Octicons as the upper GitHub Stats Extended pins. Repository names come from GitHub; the localized descriptions and real release information are retained. Repositories without a primary language show their Stars without an invented `Source` language. The adapted pin layout and icons are credited to [GitHub Stats Extended's repo renderer](https://github.com/stats-organization/github-stats-extended/blob/master/packages/core/src/cards/repo.ts); its MIT notice is retained at `assets/licenses/github-stats-extended.txt`.

The generation job uploads a short-lived artifact. Branch runs produce reviewable artifacts only. On `main`, the publisher validates all 39 SVGs, copies an exact filename allowlist, and commits only `assets/generated/`. An incomplete or failed render never replaces the checked-in cards. Publishing does not force-push or modify branch protection.

The upstream Metrics recent-languages analyzer assumes `PushEvent.payload.commits`, which was absent during live validation and caused a TypeError. The recent-languages card therefore uses the bounded public commit API above.

The Metrics contribution/status combination also exceeded the acceptable refresh time during live validation. All repository-generated cards now use bounded public API requests and native standard-library SVG renderers, with no avatar downloads, repository cloning, Docker builds, or upstream rendering action. `generate_articles.py` collects data and controls publication; `render_visuals.py` implements the approved layouts.

## Joint authorship

Every automated data commit uses the GitHub Actions bot as its author and this exact GitHub-recognized trailer:

```text
Co-authored-by: Tangyixiao <115929632+tangyixiao@users.noreply.github.com>
```

The message is defined once in `scripts/profile-cards/generate_articles.py` and written to a file for `git commit --file`. A test passes the actual message to `git interpret-trailers --parse`. Unchanged cards do not create an empty commit.

## Live services

- Overview, repository language distribution, and project pins: [GitHub Stats Extended](https://github.com/stats-organization/github-stats-extended). The overview also shows merged PR count and percentage. The language card keeps its original repository scope, including archives.
- Streak: [GitHub Readme Streak Stats](https://github.com/DenverCoder1/github-readme-streak-stats).
- Recent contribution curve: [GitHub Readme Activity Graph](https://github.com/Ashutosh00710/github-readme-activity-graph), using its current Workers endpoint on desktop (31 days). Mobile uses the generated 14-day calendar chart above, with its own explicitly labeled range.
- Project release / last-commit badges: [Shields](https://shields.io).

No Codeforces, Luogu, or other OI statistics widgets are added. These choices do not remove the existing learning/project descriptions from the README.

## Upstream versions and licenses

- Calendar projection reference: Metrics `366f8b9dfe3a59656c67d5dcad9950f59c9bc96d`, MIT, lowlighter.
- Logarithmic height reference: github-profile-3d-contrib `e235d118909be71eb7edb05482a3de4e76156df3`, MIT, SATO Yoshiyuki. The native layout adapts its `log10(count / 20 + 1) * 144 + 3` height formula.
- Official source license texts are retained in `assets/licenses/`.

The original text license does not cover third-party cards, screenshots or generated upstream assets. Refer to `CONTENT-LICENSE.md` and `assets/README.md`.
