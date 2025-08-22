---
layout: page
title: teaching
permalink: /teaching/
description: A collection of courses I have taught since 2021.
nav: true
nav_order: 3
display_categories: [Texas A&M University] # Add more universities if needed University of Arizona,
horizontal: false
---

<!-- pages/teaching.md -->

<div class="projects">
{% if site.enable_course_categories and page.display_categories %}
  <!-- Display categorized teaching courses -->
  {% for category in page.display_categories %}
  <a id="{{ category }}" href=".#{{ category }}">
    <h2 class="category">{{ category }}</h2>
  </a>
  {% assign categorized_courses = site.courses | where: "category", category %}
  {% assign sorted_courses = categorized_courses | sort: "importance" %}
  {% assign visible_courses = sorted_courses | where_exp: "course", "course.hidden != true" %}
  <!-- Generate cards for each course -->
    {% if page.horizontal %}
      <div class="container">
        <div class="row row-cols-1 row-cols-md-2">
          {% for course in visible_courses %}
            {% include courses_horizontal.liquid %}
          {% endfor %}
        </div>
      </div>
    {% else %}
      <div class="row row-cols-1 row-cols-md-2">
        {% for course in visible_courses %}
          {% include courses.liquid %}
        {% endfor %}
      </div>
    {% endif %}
  {% endfor %}
{% else %}

<!-- Display courses without categories -->

{% assign sorted_courses = site.courses | sort: "importance" %}

  <!-- Generate cards for each course -->

{% if page.horizontal %}

  <div class="container">
    <div class="row row-cols-1 row-cols-md-2">
    {% for course in sorted_courses %}
      {% include courses_horizontal.liquid %}
    {% endfor %}
    </div>
  </div>
  {% else %}
  <div class="row row-cols-1 row-cols-md-3">
    {% for course in sorted_courses %}
      {% include courses.liquid %}
    {% endfor %}
  </div>
  {% endif %}
{% endif %}
</div>
