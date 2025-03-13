---
layout: page
title: projects
permalink: /projects/
description: A growing collection of cool GDGT projects from marine sediment studies.
nav: true
nav_order: 2
display_categories: [work] #, fun
horizontal: false
---

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
