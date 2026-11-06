---
layout: page
title: A nutrient effect on the TEX₈₆ paleotemperature proxy
description: Nutrient stress leaves a warm bias in sedimentary TEX₈₆, an effect seen in cultures that we show is also recorded in seafloor sediments.
img: assets/img/projects/nutrient-effect/thumb.png
img_alt: "Global map of coretop TEX86 residuals over modern thermocline nitrate"
permalink: /projects/nutrient-effect/
importance: 3
category: work
status: published
venue: Geophysical Research Letters
venue_abbr: GRL
volume: 52
year: 2025
authors: R. Rattanasriampaipong, J. E. Tierney, J. T. Abell, L. D. Gilmore
doi: 10.1029/2025GL115237
pdf: rattanasriampaipong25-GRL-nutrient-effect-on-tex.pdf
links:
  - { label: Data, icon: fa-solid fa-database, url: "https://doi.org/10.5281/zenodo.14806961" }
  - { label: News, icon: fa-regular fa-newspaper, url: "/news/Rattanasriampaipong25_GRL/" }
bib_key: Rattanasriampaipong2025
related_publications: true
hidden: false
---

{% include project_meta.liquid %}

## In brief

<p class="project-lead">
Lab cultures show that when marine archaea are short of nutrients they build more rings into their membrane lipids, which raises TEX<sub>86</sub> as if the water were warmer. This study shows that the same &ldquo;nutrient effect&rdquo; is recorded in seafloor sediments, and that it can be separated from the temperature signal.
</p>

## Key findings

- **A global signal.** In an expanded coretop database, TEX<sub>86</sub> residuals (what is left after removing the thermal effect) correlate negatively with nitrate: &rho; = &minus;0.31 (P &lt; 0.001). Low-nutrient sediments read too warm.
- **Stronger where nitrate gradients are steep.** In regions with sharp nutrient gradients the correlation reaches &rho; = &minus;0.73 to &minus;0.91.
- **A simpler explanation for the Red Sea.** Its anomalously high TEX<sub>86</sub> fits extreme nutrient stress in an oligotrophic sea, without needing endemic archaeal clades.
- **Visible in the past.** In the Arabian Sea, TEX<sub>86</sub> warms by up to 7&nbsp;&deg;C during the Younger Dryas and Heinrich Stadial 1, when alkenone (U<sup>K&prime;</sup><sub>37</sub>) records cool and &delta;<sup>15</sup>N points to weaker upwelling and fewer nutrients. In the Tasman Sea, interglacial TEX<sub>86</sub> temperatures overshoot U<sup>K&prime;</sup><sub>37</sub> as the nutrient-poor subtropical gyre expands.

## Key figure

{%
  include figure.liquid
  path="assets/img/projects/nutrient-effect/fig1.png"
  alt="Panel a: coretop TEX86 against thermocline-integrated temperature. Panel b: TEX86 residuals against nitrate on a log scale. Panel c: world map of coretop TEX86 residuals over modern nitrate."
  class="img-fluid rounded project-figure"
  loading="eager"
  zoomable=true
  caption="<strong>Figure 1.</strong> Positive TEX<sub>86</sub> residuals in coretop sediments match low-nutrient regions. (a) TEX<sub>86</sub> against thermocline-integrated temperature. (b) Residuals from that fit fall as nitrate rises, most clearly below 2.7&nbsp;&micro;mol/L (blue). (c) Map of residuals over modern nitrate. Rattanasriampaipong et al. (2025), <em>GRL</em>."
%}

## From finding to predictor &rarr; TEXAS

<div class="project-callout">
<p>Nitrate became one of the two nonthermal predictors in {% assign texas_page = site.projects | where: "slug", "texas" | first %}{% if texas_page %}<a href="{{ texas_page.url | relative_url }}">TEXAS</a>{% else %}TEXAS{% endif %}, our proxy system model for TEX<sub>86</sub> paleothermometry. Below 1&nbsp;&micro;mol/L it shifts the TEXAS S-curve to account for nutrient stress, and the Tasman Sea records from this paper return as a TEXAS case study.</p>
</div>

## Cite

{% cite Rattanasriampaipong2025 %}. Data: [10.5281/zenodo.14806961](https://doi.org/10.5281/zenodo.14806961).
