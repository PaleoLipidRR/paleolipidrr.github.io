---
layout: page
permalink: /publications/
title: publications
description: publications by categories in reversed chronological order
nav: true
nav_order: 4
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

### manuscripts **submitted, under review, preprints and/or in-press**

<div class="publications">
  {% bibliography --file preprints %}
</div>

### manuscripts **in preparation**

<div class="publications">
  {% bibliography --file inpreps %}
</div>