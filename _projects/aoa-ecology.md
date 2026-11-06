---
layout: page
title: Archaeal lipids track AOA ecology and evolution
description: The GDGT-2/GDGT-3 ratio separates shallow and deep ecotypes of marine ammonia-oxidizing archaea, a fingerprint we trace back to the Mesozoic.
img: assets/img/png/fig3_PNAS_SPM_GMM_revised.png
img_alt: "Gaussian mixture model clusters of GDGT-2/GDGT-3 against TEX86 for shallow and deep samples"
permalink: /projects/aoa-ecology/
importance: 2
category: work
status: published
venue: Proceedings of the National Academy of Sciences
venue_abbr: PNAS
volume: 119
year: 2022
authors: R. Rattanasriampaipong, Y. G. Zhang, A. Pearson, B. P. Hedlund, S. Zhang
doi: 10.1073/pnas.2123193119
pdf: rattanasriampaipong-et-al-2022-archaeal-lipids-pnas.pdf
links: []
bib_key: rattanasriampaipong2022pnas
related_publications: true
hidden: false
---

{% include project_meta.liquid %}

## In brief

<p class="project-lead">
Archaeal membrane lipids (GDGTs) are best known as a paleothermometer, but they also carry a record of which archaea made them. By comparing published GDGTs from laboratory cultures of marine and hot-spring archaea, modern seawater and sediments, and ancient sediments up to 192 million years old, we separate the &ldquo;thermal&rdquo; behavior of these lipids from an ecological fingerprint of shallow- and deep-water ammonia-oxidizing archaea (AOA).
</p>

## Key findings

- **A presumed temperature-dependent (PTD) trend.** If temperature alone controlled lipid synthesis, TEX<sub>86</sub> would rise and GDGT-2/GDGT-3 would fall as water warms. Cultured AOA and shallow-water samples follow that trend.
- **Shallow vs. deep ecotypes.** Samples from below the pycnocline break away from the PTD trend: deep AOA raise GDGT-2/GDGT-3 and blur its link to temperature.
- **Gaussian mixture models** turn these patterns into statistical fingerprints of AOA ecology that can be applied to paleo-GDGT records.
- **AOA niche expansion.** Long-term GDGT-2/GDGT-3 trends suggest today&rsquo;s deep-water AOA were suppressed during Mesozoic&ndash;early Cenozoic greenhouse climates and expanded with later oceanographic and climate change.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/png/fig2_PNAS_GDGTdistributions_revised-01.png" title="Lipid distributions reflect archaea ecology fingerprints" alt="GDGT distributions across cultures, suspended particulate matter and sediments, with the presumed thermal-dependent trend shaded" class="img-fluid rounded z-depth-1 project-figure" zoomable=true %}
    </div>
</div>
<div class="caption">
    Distribution patterns of archaeal membrane lipids across different archives. The &lsquo;presumed thermal dependent&rsquo; trend is shown by the shaded gray bars, where higher TEX<sub>86</sub> goes with lower GDGT-2/GDGT-3 ratios.
</div>

## From finding to predictor &rarr; TEXAS

<div class="project-callout">
<p>GDGT-2/GDGT-3 became one of the two nonthermal predictors in {% assign texas_page = site.projects | where: "slug", "texas" | first %}{% if texas_page %}<a href="{{ texas_page.url | relative_url }}">TEXAS</a>{% else %}TEXAS{% endif %}, our proxy system model for TEX<sub>86</sub> paleothermometry, where it accounts for lipids from deep-water archaea. The glacial&ndash;interglacial case study at MD98-2152 and U1482 shows it at work.</p>
</div>

## Cite

{% cite rattanasriampaipong2022pnas %}
