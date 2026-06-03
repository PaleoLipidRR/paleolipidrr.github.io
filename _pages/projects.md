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

<!-- pages/projects.md -->

<div class="projects-hero">
  <h1>Exploring new insights from a comprehensive global archaeal lipid compilation</h1>
  <p>GDGT membrane lipids across cultures, the water column, and marine sediments — spanning 0 to 192 Ma.</p>
</div>

{% include research_program_diagram.liquid %}

<div class="projects">
{% if site.enable_project_categories and page.display_categories %}
  <!-- Display categorized projects -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_projects = site.projects | where: "category", category %}
  {% assign sorted_projects = categorized_projects | sort: "importance" %}
  {% assign visible_projects = sorted_projects | where_exp: "project", "project.hidden != true" %}
  <!-- Generate cards for each project -->
    {% if page.horizontal %}
      <div class="container">
        <div class="row row-cols-1 row-cols-md-2">
          {% for project in visible_projects %}
            {% include projects_horizontal.liquid %}
          {% endfor %}
        </div>
      </div>
    {% else %}
      <div class="row row-cols-1 row-cols-md-2">
        {% for project in visible_projects %}
          {% include projects.liquid %}
        {% endfor %}
      </div>
    {% endif %}
  {% endfor %}
{% else %}

<!-- Display projects without categories -->

{% assign sorted_projects = site.projects | sort: "importance" %}

  <!-- Generate cards for each project -->

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-2">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>
