# Projects Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the al-folio `/projects/` page into a research-program hub — a hero, a relationship diagram (compilation → PNAS + GRL → TEXAS), and status-badged project cards.

**Architecture:** Pure Jekyll/Liquid + SCSS, no JS. The diagram is a self-contained include with a scoped `<style>` (theme-variable colors, survives PurgeCSS because inline styles are never purged). Status is an opt-in `status:` front-matter field rendered as a pill by the card includes, styled by one new SCSS partial. Cards are the existing al-folio collection loop; we rename one project, add two, and delete eight demo files.

**Tech Stack:** Jekyll, Liquid, SCSS (al-folio theme), Bootstrap grid. Build: `bundle exec jekyll build`. Reference spec: `docs/superpowers/specs/2026-06-03-projects-page-redesign-design.html`.

**Branch:** Work continues on `projects-page-redesign` (already checked out).

**Testing note (static site):** There is no unit-test framework for Liquid. The "test" for each task is: run `bundle exec jekyll build` (must succeed with no Liquid errors) and `grep` the generated `_site/` HTML to assert the expected markup is present/absent. `_site/` is gitignored, so it is never committed.

---

### Task 1: Rename the AOA-ecology (PNAS) project and add its status

**Files:**
- Rename: `_projects/1_project.md` → `_projects/aoa-ecology.md`
- Modify: `_projects/aoa-ecology.md` (front-matter)

- [ ] **Step 1: Rename the file (preserves git history)**

```bash
git mv _projects/1_project.md _projects/aoa-ecology.md
```

- [ ] **Step 2: Add `status: published` to the front-matter**

Edit the front-matter of `_projects/aoa-ecology.md` so it reads exactly:

```yaml
---
layout: page
title: Archaeal lipids track AOA ecology and evolution
description: Proceedings of National Academy of Sciences
img: assets/img/png/fig3_PNAS_SPM_GMM_revised.png
importance: 1
category: work
status: published
related_publications: false
hidden: false
---
```

(Only the `status: published` line is added; the body of the file is unchanged.)

- [ ] **Step 3: Build**

Run: `bundle exec jekyll build`
Expected: completes with `done in N seconds`, no Liquid/Markdown errors.

- [ ] **Step 4: Verify the new URL exists and the old one is gone**

Run: `test -d _site/projects/aoa-ecology && test ! -d _site/projects/1_project && echo OK`
Expected: prints `OK`.

- [ ] **Step 5: Commit**

```bash
git add -A _projects/
git commit -m "Rename PNAS project to aoa-ecology; mark published"
```

---

### Task 2: Status-badge mechanism (SCSS + card includes)

**Files:**
- Create: `_sass/_projects.scss`
- Modify: `assets/css/main.scss` (add to `@import` list)
- Modify: `_includes/projects.liquid`
- Modify: `_includes/projects_horizontal.liquid`

- [ ] **Step 1: Create the SCSS partial**

Create `_sass/_projects.scss`:

```scss
// _sass/_projects.scss
// Opt-in status badge for project cards (rendered when a project sets `status:`).

.project-status {
  display: inline-block;
  margin-bottom: 0.4rem;
  padding: 0.1rem 0.6rem;
  border-radius: 1rem;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: #fff;

  &--published {
    background-color: #2a9d57;
  }

  &--preprint {
    background-color: var(--global-theme-color);
  }

  &--in-progress {
    background-color: #c9851f;
    color: #1d1d1f;
  }
}
```

- [ ] **Step 2: Wire the partial into the stylesheet**

In `assets/css/main.scss`, add `"projects",` to the `@import` list. Change:

```scss
  "typograms",
```

to:

```scss
  "typograms",
  "projects",
```

- [ ] **Step 3: Render the badge in the vertical card include**

In `_includes/projects.liquid`, change:

```liquid
      <div class="card-body">
        <h2 class="card-title">{{ project.title }}</h2>
```

to:

```liquid
      <div class="card-body">
        {% if project.status %}
          <span class="project-status project-status--{{ project.status }}">{{ project.status | replace: '-', ' ' | capitalize }}</span>
        {% endif %}
        <h2 class="card-title">{{ project.title }}</h2>
```

- [ ] **Step 4: Render the badge in the horizontal card include (parity)**

In `_includes/projects_horizontal.liquid`, change:

```liquid
          <div class="card-body">
            <h3 class="card-title">{{ project.title }}</h3>
```

to:

```liquid
          <div class="card-body">
            {% if project.status %}
              <span class="project-status project-status--{{ project.status }}">{{ project.status | replace: '-', ' ' | capitalize }}</span>
            {% endif %}
            <h3 class="card-title">{{ project.title }}</h3>
```

- [ ] **Step 5: Build**

Run: `bundle exec jekyll build`
Expected: success, no SCSS or Liquid errors.

- [ ] **Step 6: Verify the badge renders on the AOA card**

Run: `grep -r "project-status--published" _site/projects/index.html`
Expected: at least one match (the AOA card, which has `status: published` from Task 1).

- [ ] **Step 7: Commit**

```bash
git add _sass/_projects.scss assets/css/main.scss _includes/projects.liquid _includes/projects_horizontal.liquid
git commit -m "Add opt-in status badge to project cards"
```

---

### Task 3: TEXAS detail page (preprint)

**Files:**
- Create: `_projects/texas.md`

- [ ] **Step 1: Create the page with front-matter and a section scaffold**

Create `_projects/texas.md`:

```markdown
---
layout: page
title: TEXAS
description: A new TEX₈₆ calibration framework — synthesizing archaeal ecology (PNAS) and nutrient effects on TEX₈₆ (GRL). Preprint under review at PALO.
img:
importance: 2
category: work
status: preprint
related_publications: false
hidden: false
---

## Overview

TEXAS is a new TEX$_{86}$ calibration framework built on the global archaeal lipid compilation. _(Placeholder — replace with your overview of the framework and its motivation.)_

## Calibration framework

_(Placeholder — describe the calibration approach and what makes it new.)_

## Archaeal ecology input

The framework incorporates the archaeal ecology and evolution lens (GDGT-2/GDGT-3) from our [AOA ecology work]({% link _projects/aoa-ecology.md %}), published in PNAS. _(Placeholder — expand on how the ecological signal enters the calibration.)_

## Nutrient effects on TEX$_{86}$

Nutrient effects on TEX$_{86}$, published in GRL, are a component of the framework. _(Placeholder — summarize the GRL result and add the DOI link.)_

## Preprint

TEXAS is currently a preprint under review at *Paleoceanography and Paleoclimatology* (PALO). _(Placeholder — add the preprint DOI/link once available.)_
```

Note: `img:` is intentionally empty (no thumbnail yet — the card renders without one). The user supplies a figure later.

- [ ] **Step 2: Build**

Run: `bundle exec jekyll build`
Expected: success. The `{% link %}` tag resolves only if `_projects/aoa-ecology.md` exists (it does, from Task 1) — a broken link would fail the build, so a clean build confirms the cross-link.

- [ ] **Step 3: Verify the TEXAS card and preprint badge render**

Run: `grep -r "project-status--preprint" _site/projects/index.html && test -d _site/projects/texas && echo OK`
Expected: a match for the preprint badge, then `OK`.

- [ ] **Step 4: Commit**

```bash
git add _projects/texas.md
git commit -m "Add TEXAS project page (preprint, under review at PALO)"
```

---

### Task 4: Hidden GDGTdb stub

**Files:**
- Create: `_projects/gdgtdb.md`

- [ ] **Step 1: Create the hidden stub**

Create `_projects/gdgtdb.md`:

```markdown
---
layout: page
title: GDGTdb
description: A global archaeal lipid (GDGT) database. In preparation — not yet public.
img:
importance: 3
category: work
hidden: true
---

_Private stub. This project is intentionally hidden. To publish: set `hidden: false` and (optionally) add a `redirect:` pointing to the standalone GDGTdb site._
```

- [ ] **Step 2: Build**

Run: `bundle exec jekyll build`
Expected: success.

- [ ] **Step 3: Verify GDGTdb is NOT listed on the projects page**

Run: `grep -c "GDGTdb" _site/projects/index.html`
Expected: `0` (the card is hidden from the listing by the existing `hidden != true` filter).

- [ ] **Step 4: Commit**

```bash
git add _projects/gdgtdb.md
git commit -m "Add hidden GDGTdb stub (publish later by flipping hidden)"
```

---

### Task 5: Delete the unused al-folio demo projects

**Files:**
- Remove: `_projects/2_project.md` … `_projects/9_project.md`

- [ ] **Step 1: Remove the eight demo files**

```bash
git rm _projects/2_project.md _projects/3_project.md _projects/4_project.md _projects/5_project.md _projects/6_project.md _projects/7_project.md _projects/8_project.md _projects/9_project.md
```

- [ ] **Step 2: Build**

Run: `bundle exec jekyll build`
Expected: success.

- [ ] **Step 3: Verify only the three real projects remain**

Run: `ls _projects/`
Expected: exactly `aoa-ecology.md  gdgtdb.md  texas.md`.

- [ ] **Step 4: Commit**

```bash
git commit -m "Remove unused al-folio demo project files"
```

---

### Task 6: Relationship diagram include + page hero

**Files:**
- Create: `_includes/research_program_diagram.liquid`
- Modify: `_pages/projects.md` (front-matter + replace hero block + add include)

- [ ] **Step 1: Create the diagram include**

Create `_includes/research_program_diagram.liquid`:

```liquid
{%- comment -%} Relationship diagram for the Projects research-program hub. {%- endcomment -%}
<div class="research-program-diagram">
  <div class="rpd-node rpd-foundation">
    <div class="rpd-title">Global archaeal lipid compilation</div>
    <div class="rpd-sub">turning rich archaeal lipid data into new insights</div>
  </div>
  <div class="rpd-connector"></div>
  <div class="rpd-branches">
    <div class="rpd-node">
      <div class="rpd-title">AOA ecology &amp; evolution</div>
      <div class="rpd-sub">PNAS &middot; GDGT-2 / GDGT-3</div>
    </div>
    <div class="rpd-node">
      <div class="rpd-title">Nutrient effects on TEX<sub>86</sub></div>
      <div class="rpd-sub">GRL</div>
    </div>
  </div>
  <div class="rpd-connector"></div>
  <div class="rpd-label">&darr; both inform the calibration</div>
  <div class="rpd-node rpd-synthesis">
    <div class="rpd-title">TEXAS</div>
    <div class="rpd-sub">new TEX<sub>86</sub> calibration framework</div>
  </div>
</div>

<style>
  .research-program-diagram {
    max-width: 440px;
    margin: 1.5rem auto 2.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .research-program-diagram .rpd-node {
    width: 100%;
    border: 1px solid var(--global-divider-color);
    border-radius: 10px;
    padding: 0.6rem 0.8rem;
    background-color: var(--global-card-bg-color);
    text-align: center;
  }
  .research-program-diagram .rpd-foundation {
    background-color: var(--global-theme-color);
    border-color: var(--global-theme-color);
    color: #fff;
  }
  .research-program-diagram .rpd-foundation .rpd-sub { color: rgba(255, 255, 255, 0.9); }
  .research-program-diagram .rpd-synthesis { border: 2px solid var(--global-theme-color); }
  .research-program-diagram .rpd-title { font-weight: 700; font-size: 0.9rem; line-height: 1.2; }
  .research-program-diagram .rpd-sub { font-size: 0.75rem; color: var(--global-text-color-light); line-height: 1.25; margin-top: 0.15rem; }
  .research-program-diagram .rpd-connector { width: 1px; height: 16px; background-color: var(--global-divider-color); }
  .research-program-diagram .rpd-branches { display: flex; gap: 0.6rem; width: 100%; }
  .research-program-diagram .rpd-branches .rpd-node { flex: 1; }
  .research-program-diagram .rpd-label { font-size: 0.8rem; font-weight: 700; color: var(--global-theme-color); margin: 0.2rem 0; }
  @media (max-width: 576px) {
    .research-program-diagram .rpd-branches { flex-direction: column; }
  }
</style>
```

- [ ] **Step 2: Replace the front-matter of `_pages/projects.md`**

Change the existing front-matter (lines 1–10) to exactly:

```yaml
---
layout: page
title: projects
permalink: /projects/
description: Exploring new insights from a comprehensive global archaeal lipid compilation.
nav: true
nav_order: 2
display_categories: [work]
horizontal: false
_styles: >
  .post-header { display: none; }
  .projects-hero { text-align: center; max-width: 640px; margin: 0 auto 0.5rem; }
  .projects-hero h1 { font-weight: 800; line-height: 1.25; margin-bottom: 0.5rem; }
  .projects-hero p { color: var(--global-text-color-light); font-size: 0.95rem; }
---
```

(The `_styles` block hides the default page header — which would otherwise print "projects" + description — and styles the custom hero. The `description` is kept for SEO/meta.)

- [ ] **Step 3: Replace the old hero block with the hero + diagram include**

In `_pages/projects.md`, delete this entire block:

```liquid
<!-- pages/projects.md -->

### **Archaeal membrane lipids as a proxy for ocean temperatures**

<div style="position: relative; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; padding-top: 400px;">
  <div style="position: relative; flex: 1;">
    <!-- Left Image (Main) -->
    <img src='{{ "/assets/img/png/archaeal_membrane_lipids.png" | relative_url }}' 
         alt="Main Image" 
         style="width: 80%;" />

    <!-- Top-Right Overlay Image -->
    <img src='{{ "/assets/img/png/archaeal_membrane_lipids_adjustement.png" | relative_url }}'
         alt="Overlay Image"
         style="position: absolute; top: -120%; right: 0; width: 70%; z-index: 2;" />

  </div>
</div>
```

and replace it with:

```liquid
<!-- pages/projects.md -->

<div class="projects-hero">
  <h1>Exploring new insights from a comprehensive global archaeal lipid compilation</h1>
  <p>GDGT membrane lipids across cultures, the water column, and marine sediments — spanning 0 to 192 Ma.</p>
</div>

{% include research_program_diagram.liquid %}
```

(The `<div class="projects"> … </div>` block that follows is left unchanged.)

- [ ] **Step 4: Build**

Run: `bundle exec jekyll build`
Expected: success, no Liquid errors (a missing include would fail here).

- [ ] **Step 5: Verify hero + diagram render and the old hack is gone**

Run:
```bash
grep -q "Exploring new insights from a comprehensive global archaeal lipid compilation" _site/projects/index.html \
  && grep -q "research-program-diagram" _site/projects/index.html \
  && grep -q "Nutrient effects on TEX" _site/projects/index.html \
  && ! grep -q "archaeal_membrane_lipids_adjustement" _site/projects/index.html \
  && echo OK
```
Expected: prints `OK`.

- [ ] **Step 6: Commit**

```bash
git add _includes/research_program_diagram.liquid _pages/projects.md
git commit -m "Add hero + relationship diagram to projects page"
```

---

### Task 7: Full verification and integration

**Files:** none (verification only)

- [ ] **Step 1: Clean build**

Run: `bundle exec jekyll build`
Expected: success.

- [ ] **Step 2: Spec checklist — confirm each item**

```bash
# Two visible cards (AOA + TEXAS), GDGTdb hidden:
grep -c "card-title" _site/projects/index.html        # expect 2
grep -c "GDGTdb" _site/projects/index.html             # expect 0
# Both badges present:
grep -o "project-status--published" _site/projects/index.html | head -1   # expect a match
grep -o "project-status--preprint"  _site/projects/index.html | head -1   # expect a match
```

- [ ] **Step 3: Visual check in a browser (light + dark + narrow)**

Run: `bundle exec jekyll serve` and open <http://localhost:4000/projects/>.
Confirm: hero headline centered; diagram diamond renders (foundation in theme color, TEXAS outlined); two cards with badges; toggle OS dark mode and confirm diagram/badges remain legible; narrow the window below 576px and confirm the two insight nodes stack and cards go single-column.

- [ ] **Step 4: Push the branch and open a PR (ask the user first)**

```bash
git push -u origin projects-page-redesign
gh pr create --fill --base main
```

Do not push or open the PR without the user's go-ahead.

---

## Self-Review

**Spec coverage:** hero (Task 6) ✓ · convergence diagram (Task 6) ✓ · TEXAS preprint card + page (Task 3) ✓ · nutrient effects as a TEXAS section (Task 3) ✓ · AOA rename + published status (Tasks 1–2) ✓ · hidden GDGTdb (Task 4) ✓ · delete demo files (Task 5) ✓ · status badge field + SCSS partial + main.scss import + both includes (Task 2) ✓ · verification incl. light/dark + responsive (Task 7) ✓.

**Placeholder scan:** the only "Placeholder" markers are intentional prose stubs inside the TEXAS page body (Task 3), which the user fills in later — every plan step itself contains complete, runnable content.

**Type/name consistency:** the CSS class `project-status` and modifiers `project-status--published` / `--preprint` / `--in-progress` match between the SCSS partial (Task 2 Step 1) and the Liquid in both includes (Task 2 Steps 3–4); the include filename `research_program_diagram.liquid` matches the `{% include %}` call (Task 6); the renamed `_projects/aoa-ecology.md` matches the `{% link %}` target in the TEXAS page (Task 3).
