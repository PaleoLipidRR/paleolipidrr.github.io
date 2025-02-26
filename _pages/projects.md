---
layout: page
title: projects
permalink: /projects/
description: A growing collection of your cool projects.
nav: true
nav_order: 3
display_categories: [work] #, fun
horizontal: false
---

<!-- pages/projects.md -->

### **Archaeal membrane lipids as a proxy for ocean temperatures**

<br>
<br>
<div class="row">
    <div class="custom-figure-container">
        {% include figure.liquid loading="eager" path="assets/img/png/archaeal_membrane_lipids_adjustement.png" title="archaeal membrane lipids adjustment" class="img-fluid custom-figure" %}
    </div> 
    <br>
    <br>
    <div class="custom-figure-container">
        {% include figure.liquid loading="eager" path="assets/img/png/archaeal_membrane_lipids.png" title="archaeal membrane lipids" class="img-fluid custom-figure" %}
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
      <div class="row row-cols-1 row-cols-md-3">
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
  <div class="row row-cols-1 row-cols-md-3">
    {% for project in sorted_projects %}
      {% include projects.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>
