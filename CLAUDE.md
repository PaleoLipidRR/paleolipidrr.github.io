# CLAUDE.md

> **What is this file?** It is a briefing for AI coding assistants such as [Claude Code](https://docs.anthropic.com/en/docs/claude-code), which read it automatically when they work in this repository. It is excluded from the built website (`_config.yml` › `exclude`).

## This repository

Ronnakrit Rattanasriampaipong's academic website, built with Jekyll on the al-folio theme and deployed to <https://paleolipidrr.github.io/> by `.github/workflows/deploy.yml` on pushes to `main`. `/TEXAS/` on the same domain is a separate GitHub Pages site (the `texas-psm` docs); see "Reserved paths" in `README.md`.

## Conventions

- Write every paragraph of prose as one line, with no line breaks inside it. Break lines only between paragraphs, list items, table rows, headings and code blocks. This applies to Markdown pages and posts, project pages, docs and notes in this repository, and PR and issue descriptions; code, Liquid templates, HTML/CSS and commit messages keep their usual formatting.
- Leave al-folio's own template files (theme docs, sample posts and news) as upstream wrote them, so theme updates merge cleanly.
- Run `npx prettier . --check` before pushing; CI enforces it.
