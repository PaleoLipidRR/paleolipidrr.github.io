# Projects Page Redesign — Design Spec

**Date:** 2026-06-03
**Site:** `paleolipidrr.github.io` (al-folio Jekyll theme)
**Author:** Ronnakrit Rattanasriampaipong (with Claude)

## Overview

Redesign the `/projects/` page from a single PNAS card into a **research-program hub** that frames the work under one overarching theme — *exploring new insights from a comprehensive global archaeal lipid compilation* — and shows how the individual projects relate. The page keeps the al-folio card system and adds two things on top: a clean hero and a relationship diagram.

The page stays part of the personal academic site (no separate standalone website). A future GDGTdb database site can be linked from a card when it exists; the structure is built to accommodate that without rework.

## Goals

- Communicate the overarching research narrative at a glance.
- Show that the published PNAS (archaeal ecology) and GRL (nutrient effects on TEX₈₆) results both feed the in-progress TEXAS calibration framework.
- Present projects as cards that link to detail pages hosted on this site.
- Keep everything backward-compatible with al-folio conventions and easy to extend as projects mature.

## Non-Goals

- No separate/standalone website (deferred until GDGTdb needs one).
- No public exposure of GDGTdb yet.
- No status-based section grouping yet (only two visible cards — the diagram carries the narrative; grouping can return when there are more projects).
- No CMS, JS framework, or backend. Plain Jekyll/Liquid + SCSS.

## Locked Decisions

| Decision | Choice |
|---|---|
| Hosting | Projects page as hub on the existing al-folio site |
| Page structure | Hero → relationship diagram → card grid |
| Diagram form | Convergence: compilation → {PNAS, GRL} → TEXAS |
| Project name | "TEXAS" (not "TEXAS PSM") |
| Card destinations | Internal detail pages (one page per project) |
| Nutrient effects (GRL) | A **section inside the TEXAS page** + a node in the diagram; **not** its own card. The TEXAS page cites/links the GRL paper. |
| GDGTdb | Hidden card stub created now (`hidden: true`); publish later by flipping the flag |
| Demo files | Delete the 8 unused al-folio demo project files (`2_project.md`–`9_project.md`) |

## Page Anatomy

`/projects/` renders three stacked zones, in order:

1. **Hero** — centered headline + one-line subtitle. Replaces the current overlapping-image block (the `padding-top: 400px` / `top: -120%` hack in `_pages/projects.md`).
   - Headline: *Exploring new insights from a comprehensive global archaeal lipid compilation*
   - Subtitle: *GDGT membrane lipids across cultures, the water column, and marine sediments — spanning 0 to 192 Ma.*

2. **Relationship diagram** — see below. Sits between the hero and the cards, **before** `<div class="projects">`, so it is outside the card grid entirely.

3. **Card grid** — the existing al-folio card loop (`_includes/projects.liquid`), unchanged in structure, now rendering two visible cards plus the hidden GDGTdb stub. Each card gains an optional status badge.

## The Relationship Diagram

A small, self-contained component expressing the scientific narrative as a "diamond": one shared dataset → two published findings → one synthesis.

```
        ┌─────────────────────────────────────────┐
        │     Global archaeal lipid compilation     │   (foundation, accent fill)
        │     the shared dataset behind every project│
        └─────────────────────┬─────────────────────┘
                              │
            ┌──────────────────┴──────────────────┐
   ┌──────────────────┐                  ┌──────────────────┐
   │ AOA ecology &    │                  │ Nutrient effects │
   │ evolution        │                  │ on TEX₈₆         │
   │ PNAS · GDGT-2/3  │                  │ GRL              │
   └──────────────────┘                  └──────────────────┘
            └──────────────────┬──────────────────┘
                  ↓ both inform the calibration
        ┌─────────────────────────────────────────┐
        │ TEXAS                                     │   (synthesis, accent outline)
        │ new TEX₈₆ calibration framework           │
        └─────────────────────────────────────────┘
```

**Node text (exact):**

- Foundation: **Global archaeal lipid compilation** / *the shared dataset behind every project*
- Insight A: **AOA ecology & evolution** / *PNAS · GDGT-2 / GDGT-3*
- Insight B: **Nutrient effects on TEX₈₆** / *GRL*
- Convergence label: *both inform the calibration*
- Synthesis: **TEXAS** / *new TEX₈₆ calibration framework*

**Implementation:**

- New include `_includes/research_program_diagram.liquid`, holding the markup plus a **scoped `<style>` block** (CSS lives with the component; no global stylesheet pollution).
- Colors use al-folio theme variables so it adapts to light/dark: `--global-theme-color` (accent fill/outline), `--global-bg-color`, `--global-card-bg-color`, `--global-text-color`, `--global-text-color-light` (sub-text), `--global-divider-color` (borders/connectors).
- **Responsive:** the two insight nodes sit side-by-side on wider screens and stack vertically below ~600px (foundation and synthesis are always full-width).
- **Optional enhancement (note, not required):** make nodes clickable — PNAS node → PNAS detail page, GRL node → GRL paper DOI, TEXAS node → TEXAS detail page.

## Project Inventory & Card Data Model

Cards are sorted by `importance` (al-folio convention). Category stays `work`; `display_categories: [work]` unchanged.

| Project | File | Visible | `importance` | `status` | Links to |
|---|---|---|---|---|---|
| Archaeal lipids track AOA ecology & evolution | `_projects/1_project.md` (existing) | yes | 1 | `published` | its detail page (existing content) + PNAS DOI |
| TEXAS | `_projects/texas.md` (new) | yes | 2 | `in-progress` | its detail page (new) |
| GDGTdb | `_projects/gdgtdb.md` (new) | no (`hidden: true`) | 3 | — | (stub; future) |

**PNAS card** — keep the existing detail page content. Add `status: published` to front-matter. Optionally surface the PNAS DOI on the page.

**TEXAS card** — new detail page with this section scaffold (placeholder prose for the user to fill):
- **Overview** — what TEXAS is (a new TEX₈₆ calibration framework built on the global compilation).
- **Calibration framework** — the core approach.
- **Archaeal ecology input** — how the AOA ecology/evolution lens (GDGT-2/GDGT-3, PNAS) is incorporated; links to the PNAS work.
- **Nutrient effects on TEX₈₆** — the GRL result and how it enters the calibration; cites/links the GRL paper.
- Card description (draft): *A new TEX₈₆ calibration framework — synthesizing the archaeal ecology lens (PNAS) and nutrient effects on TEX₈₆ (GRL).*

**GDGTdb stub** — minimal page, `hidden: true`, so it never renders publicly. Publishing later = set `hidden: false` and (optionally) add a `redirect:` to its standalone site.

## Status Badge

A small, opt-in badge on each card indicating maturity.

- **Front-matter:** optional `status:` field on project files. Recognized values: `published`, `in-progress`. Absent → no badge (backward-compatible with all existing/future cards).
- **Render:** in `_includes/projects.liquid`, a pill at the top of `.card-body` (above the title) shown only when `project.status` is set. Robust whether or not the card has an image. (This refines the visual mockup, which floated the badge over the image — the card-body position works for image-less cards too.)
- **Style:** a short SCSS rule in a new partial `_sass/_projects.scss`, wired in by adding `"projects",` to the `@import` list in `assets/css/main.scss`. `published` → green; `in-progress` → amber. Text legible in light/dark.
- Mirror change in `_includes/projects_horizontal.liquid` for consistency (the page uses `horizontal: false`, but keeping the two includes in sync avoids surprises if the flag is ever flipped).

## File-by-File Changes

**New**
- `_includes/research_program_diagram.liquid` — the diagram component (markup + scoped CSS).
- `_projects/texas.md` — TEXAS detail page (front-matter + section scaffold).
- `_projects/gdgtdb.md` — hidden GDGTdb stub.
- `_sass/_projects.scss` — status-badge styles (imported into the main stylesheet).

**Changed**
- `_pages/projects.md` — remove the overlapping-image hero; add the clean hero markup and `{% include research_program_diagram.liquid %}` before `<div class="projects">`. Card loop unchanged.
- `_includes/projects.liquid` — render the optional status badge.
- `_includes/projects_horizontal.liquid` — render the optional status badge (parity).
- `_projects/1_project.md` — add `status: published`.
- `assets/css/main.scss` — add `"projects",` to the `@import` list (wires in the new partial).

**Removed**
- `_projects/2_project.md` … `_projects/9_project.md` — eight unused al-folio demo cards (all `hidden: true` boilerplate).

## Content the User Provides Later (not blockers)

- A thumbnail image for the TEXAS card (a placeholder is wired in until then).
- Final body text/figures for the TEXAS detail page (scaffold + placeholder prose ships first).
- The GRL and PNAS DOIs/links to wire into the TEXAS page and PNAS page.

## Verification

- `bundle exec jekyll build` succeeds with no Liquid errors.
- Local serve: `/projects/` shows hero → diagram → two cards (PNAS, TEXAS); GDGTdb does **not** appear.
- Diagram renders correctly in both light and dark themes and stacks on a narrow viewport.
- Status badges show on both cards; a card with no `status` shows none.
- No console errors; existing pages unaffected.

## Future / Out of Scope

- Standalone GDGTdb website (link from its card via `redirect:` when ready).
- Status-based section grouping once the visible project count grows.
- Making diagram nodes clickable links.
