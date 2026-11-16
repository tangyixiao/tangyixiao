# Profile card generation

The public profile embeds live project/version cards and contribution graphs, plus SVGs generated in this repository. The profile itself has no service footnotes.

## Generated images

`.github/workflows/profile-cards.yml` runs daily at 22:17 UTC (06:17 Asia/Shanghai), on generator changes, and on manual dispatch. The generation job has read-only repository permission; only the separate `main` publishing job can write generated images.

| File | Source and scope |
| --- | --- |
| `assets/generated/isometric.svg` | The official lowlighter/metrics isocalendar plugin, using the public contribution calendar for a full year. Upstream labels are normalized from “Commits” to “Contributions” because the calendar also counts PRs and issues. |
| `assets/generated/development.svg` | One public GraphQL query: up to 20 external repositories contributed to in the past year (COMMIT, ISSUE, PULL_REQUEST; up to ten names displayed), plus issue and PR states in two explicitly labeled scopes: public repositories owned by the user, and public items authored by the user. Open, closed-unmerged and merged PR counts are disjoint. |
| `assets/generated/recent-languages.svg` | Changed lines (additions + deletions) in recognized code/markup files from up to 30 public commit-search results in the last 14 days, up to 100 files per commit. Top eight languages are shown; percentages use the full recognized sample as denominator. Generated profile images and prose/data/config extensions are excluded. This bounded activity sample is not total authored code, proficiency or time. |
| `assets/generated/contribution-3d-{light,dark}.svg` | Official github-profile-3d-contrib, using the supplied light/dark palette and public data accessible to the repository token. |
| `assets/generated/articles.svg` | Up to four real posts, ordered by frontmatter date and slug, from the public `blog-src` directory of `tangyixiao/tangyixiao.github.io`. Dates and titles are not inferred from Git commit timestamps. |
| `assets/generated/activity-mobile.svg` | Fourteen daily counts from the public contribution calendar, rendered at a native 420px width so mobile axis labels remain readable. |

The generation job uploads a short-lived artifact. Branch runs produce reviewable artifacts only. On `main`, the publisher validates all seven SVGs, copies an exact filename allowlist, and commits only `assets/generated/`. An incomplete or failed render never replaces the checked-in cards. Publishing does not force-push or modify branch protection.

The upstream Metrics recent-languages analyzer assumes `PushEvent.payload.commits`, which was absent during live validation and caused a TypeError. The recent-languages card therefore uses the bounded public commit API above.

The Metrics contribution/status combination also exceeded the acceptable refresh time during live validation. The contribution/status card now uses the single bounded GraphQL query above, with no avatar downloads or repository cloning. Only the isometric calendar uses Metrics; the 3D landscape uses its dedicated official action.

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

- Metrics isocalendar action: `366f8b9dfe3a59656c67d5dcad9950f59c9bc96d`, MIT, lowlighter. The official action uses its upstream prebuilt container; its actual image digest is visible in generation logs.
- 3D contribution action: `e235d118909be71eb7edb05482a3de4e76156df3`, MIT, SATO Yoshiyuki.
- Official source license texts are retained in `assets/licenses/`.

The original text license does not cover third-party cards, screenshots or generated upstream assets. Refer to `CONTENT-LICENSE.md` and `assets/README.md`.
