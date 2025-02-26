---
layout: page
permalink: /publications/
title: publications
description: publications by categories in reversed chronological order
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

### papers published in **refereed journals**

<div class="publications">

{% bibliography --file papers %}

</div>
<br>
<br>

### manuscripts in <br>

#### **preparation, submitted, under review,**<br> **under revisions, preprints and/or in-press**

<div class="publications">
  {% bibliography --file preprints %}
</div>