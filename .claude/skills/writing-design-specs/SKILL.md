---
name: writing-design-specs
description: Use when authoring or saving a design spec or design document in this repo — including the spec produced at the end of a brainstorming session, or any file under docs/superpowers/specs/. Excludes implementation plans, which stay markdown.
---

# Writing Design Specs (HTML)

## Overview

In this repository, **design specs are standalone HTML documents** — not markdown. A spec describes *what* we are building and *why* (goals, decisions, architecture, mockups). Authoring it as HTML lets the spec embed the actual rendered diagrams and page mockups produced during brainstorming, instead of ASCII approximations or screenshots.

**Implementation plans stay markdown** (see superpowers:writing-plans). Specs = HTML; plans = MD.

## Quick Reference

| Artifact | Format | Location |
|---|---|---|
| Design spec / design doc | HTML | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.html` |
| Implementation plan | Markdown | per superpowers:writing-plans |

## Authoring an HTML Spec

1. **Self-contained.** One `.html` file with an inline `<style>` block and no external CSS/JS/CDN dependencies, so it renders correctly opened directly (`file://`) or served anywhere.
2. **Same content a written spec needs**, as semantic HTML: overview, goals/non-goals, locked decisions, page/architecture, components, file-by-file changes, verification, out-of-scope.
3. **Embed visuals as live HTML/CSS** — reuse the diagrams and mockups built during brainstorming (e.g., the visual-companion screens). Render them inline; do not paste screenshots or ASCII art.
4. **Readable + responsive.** Constrain content width, support light/dark via `prefers-color-scheme` where practical, and let embedded mockups reflow on narrow screens.
5. Keep prose tight; let the embedded visuals carry structure that prose would labor to describe.

## Common Mistakes

| Mistake | Fix |
|---|---|
| External stylesheet/CDN link in the spec | Inline all CSS; the file must stand alone |
| Writing the spec in markdown out of habit | Specs are HTML in this repo |
| Writing the implementation *plan* in HTML | Plans stay markdown |
| Pasting a screenshot of a diagram | Embed the live HTML/CSS diagram instead |

## Related

- **superpowers:brainstorming** produces the spec's content and the mockups to embed.
- **superpowers:writing-plans** produces the markdown implementation plan after the spec is approved.
