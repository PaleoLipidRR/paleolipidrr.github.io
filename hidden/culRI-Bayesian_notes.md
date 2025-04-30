---
layout: default
title: culRI-Bayesian notes
permalink: /hidden/culRI-Bayesian_notes.html
---
<meta name="robots" content="noindex">

<style>
  /* Copy-button flash states */
  .code-display-wrapper button.copy:active i.fa-clipboard,
  .code-display-wrapper button.copy.clicked i.fa-clipboard {
    color: #E53E3E !important;
  }
  .code-display-wrapper button.copy.clicked i.fa-clipboard {
    color: #48BB78 !important;
  }

  /* Code block styling */
  pre {
    background: #1e1e1e;
    padding: 1em;
    border-radius: 0.5em;
    overflow-x: auto;
  }
  pre code {
    font-size: 1.1em;
    line-height: 1.4;
    background: #1e1e1e !important;
  }

  /* File-explorer window styles */
  .page-container {
    display: flex;
    height: 600px;
    border: 1px solid #ddd;
    margin-top: 2em;
  }
  .sidebar {
    width: 200px;
    background: #f7f7f7;
    border-right: 1px solid #ccc;
    overflow-y: auto;
    padding: 1em;
  }
  .sidebar a {
    display: block;
    margin: 0.5em 0;
    color: #0366d6;
    text-decoration: none;
  }
  .sidebar a.selected,
  .sidebar a:hover {
    text-decoration: underline;
  }
  .content {
    flex: 1;
    padding: 1em;
    overflow-y: auto;
  }
  .content section {
    display: none;
  }
  .content section.active {
    display: block;
  }
  /* Override code block inside content pane */
  .content pre {
    background: #2d2d2d;
    color: #f8f8f2;
    border-radius: 4px;
  }

  /* only indent the first level of nesting */
  details > details {
    margin-left: 1.5em;
  }

  /* if you want deeper levels to indent further, chain the > again */
  details > details > details {
    margin-left: 3em;
  }

  /* and if you only want to shift the summary line */
  details > details > summary {
    padding-left: 1.5em;
  }
  details > ul {
    margin: 0.5em 0 0 1em;   /* indent the list inside the dropdown */
    list-style-type: disc;   /* you can choose circle, square, decimal, etc. */
  }
  details > ul > li {
    margin-bottom: 0.25em;
  }

</style>

<!-- Syntax highlighting with Highlight.js VS Code theme -->
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/atom-one-dark.min.css">

<script
  src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js">
</script>
<script>hljs.highlightAll();</script>

<script>
  document.querySelectorAll('.code-display-wrapper button.copy').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.classList.add('clicked');
      setTimeout(() => btn.classList.remove('clicked'), 800);
    });
  });
</script>

# **Bayesian Analysis Notes**
## Developing the new temperature calibration model using Ring Index.

This page contains notes for the **cul**ture-informed temperature calibration model using **R**ing **I**ndex using **Bayesian** inference approach. The model is called **culRI-Bayesian** (to make it a homophone of "calibration").

Based on the Temperature-RI distribution across all archives---**cultures, mesocosms, and coretop**---the **logistic functio with a fixed upper asymptote** (see the interactive plot to see how each hyperparameter impacts the curve) is selected because:
- RI values of lab cultures at growth T < 10&deg;C and T > 35&deg;C are flatten out---RI values are less sensitive to change in T (see Figure 1).
- The upper asymptote is fixed to 1.0, which is the theoretical maximum RI value for all cultures at the highest growth T (35&deg;C).
- The logistic function has been widely used in ecology to describe the growth of populations or the response of organisms to environmental factors. 

<details style="margin-left: 3em;">
  <summary>
    <span style="font-size:1em; font-weight:400;">
      Below are examples of studies highlighting the use of logistic function to describe growth curves:
    </span>
  </summary>
  <ul>
    <li>
      Harrold, Z. R., Skidmore, M. L., Hamilton, T. L., Desch, L., Amada, K.,
      Van Gelder, W., … & Boyd, E. S. (2016). Aerobic and anaerobic thiosulfate
      oxidation by a cold-adapted, subglacial chemoautotroph. 
      <em>Applied and Environmental Microbiology</em>, 82(5), 1486–1495. 
      <a href="https://doi.org/10.1128/AEM.03398-15"
         target="_blank" rel="noopener">
        https://doi.org/10.1128/AEM.03398-15
      </a>
    </li>
    <li>
      Goehlich, H., Luna-Jorquera, G., Drapeau Picard, A. P., Pantoja, J., Tala, F.,
      & Thiel, M. (2024). Seasonal growth rates of gooseneck barnacles (Lepas spp.):
      Proxies for floating time of rafts in marine ecosystems. 
      <em>Marine Biology</em>, 171(1), 36. 
      <a href="https://doi.org/10.1007/s00227-023-04336-8"
         target="_blank" rel="noopener">
        https://doi.org/10.1007/s00227-023-04336-8
      </a>
    </li>
    <li>
      Jenkins, D. G., & Pierce, S. (2017). General allometric scaling of net primary
      production agrees with plant adaptive strategy theory and has tipping points.
      <em>Journal of Ecology</em>, 105(4), 1094–1104. 
      <a href="https://doi.org/10.1111/1365-2745.12726"
         target="_blank" rel="noopener">
        https://doi.org/10.1111/1365-2745.12726
      </a>
    </li>
    <li>
      Sauve, D., Friesen, V. L., Hatch, S. A., Elliott, K. H., & Charmantier, A. (2023).
      Shifting environmental predictors of phenotypes under climate change: a case
      study of growth in high latitude seabirds. 
      <em>Journal of Avian Biology</em>, 2023(5-6), e03062. 
      <a href="https://doi.org/10.1111/jav.03062"
         target="_blank" rel="noopener">
        https://doi.org/10.1111/jav.03062
      </a>
    </li>
    <li>
      [Book Chapter] Vallina, S. M., Martinez-Garcia, R., Smith, S. L., & Bonachela, J. A.
      (2019). Models in microbial ecology. <em>Academic Press</em>. 
      <a href="https://doi.org/10.1016/B978-0-12-809633-8.20789-9"
         target="_blank" rel="noopener">
        https://doi.org/10.1016/B978-0-12-809633-8.20789-9
      </a>
    </li>
  </ul>
</details>
<br>
The model is implemented using [**Stan**](https://mc-stan.org/), a probabilistic programming language for Bayesian inference. The model is fit to the data using Markov Chain Monte Carlo (MCMC) sampling.

<!-- Interactive plot of logistic functional forms -->
<details>
  <summary>
    <span style="font-size:1.25em; font-weight:600;">Logistic functional forms (interactive plot)
    </span>
  </summary>
<iframe
  src="/assets/html/logistic_fixed_upper_interactive.html"
  width="100%"
  height="600"
  frameborder="0"
></iframe>
</details>
<br>
{% assign deeptealdot = '<span style="color: #006D6D">&#9679;</span>' %}
{% assign tealdot = '<span style="color:teal">&#9679;</span>' %}
{% assign orangedot = '<span style="color:orange">&#9679;</span>' %}
{% assign graydot = '<span style="color:gray">&#9679;</span>' %}


| Model Name | T | scaled RI | gdgt23ratio | x0 | k | b | beta0 | beta1 |
|------------|:--:|:---------:|:--------:|:----:|:-----:|:-----:|:-----:|:----:|
| **joint-cul-meso** | {{ deeptealdot }} {{ tealdot }} | {{ deeptealdot }} {{ tealdot }} | | {{ graydot }} | {{ graydot }} | {{ graydot }} | | |
| **joint-cul-meso-coretop** | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | | {{ graydot }} | {{ graydot }} | {{ graydot }} | | |
| **joint-cul-meso-coretop-multivariate** | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ orangedot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} |
| **joint-cul-meso-coretop-multivariate-fixedbeta1** | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ orangedot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | |
| **joint-all-full-multivariate** | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} |
| **joint-all-full-multivariate-fixedbeta1** | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ deeptealdot }} {{ tealdot }} {{ orangedot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | {{ graydot }} | |

<br>
**Legend** | {{ deeptealdot }} Culture --- {{ tealdot }} Mesocosm --- {{ orangedot }} Coretop

{% comment %}
  Grab every static file whose path contains '/hidden/stan_files/'
  (we assume you only put .stan files in there)
{% endcomment %}
{% assign stanfiles = site.static_files 
   | where_exp: "f", "f.path contains '/hidden/stan_files/'" %}

<details>
  <summary>
    <span style="font-size:1.25em; font-weight:600;">
    Stan model files
    </span>
  </summary>
  <div class="page-container">
    <nav class="sidebar">
      <strong>Stan files</strong>
      {% for f in stanfiles %}
        <a href="#{{ f.name | slugify }}">{{ f.name }}</a>
      {% endfor %}
    </nav>

    <div class="content">
      {% for f in stanfiles %}
        <section id="{{ f.name | slugify }}">
          <h3>{{ f.name }}</h3>
          {%- comment -%}
            include_relative is relative to the .md file,
            so if your page is at hidden/culRI-Bayesian_notes.md
            and your files live in hidden/stan_files/, do:
          {%- endcomment -%}

          <pre><code class="language-stan">
  {% include_relative stan_files/{{ f.name }} %}
          </code></pre>

        </section>
      {% endfor %}
    </div>
  </div>
</details>
<script>
  // same tabbing logic as before
  const links = document.querySelectorAll('.sidebar a');
  const sections = document.querySelectorAll('.content section');
  links.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      sections.forEach(s => s.classList.remove('active'));
      links.forEach(l => l.classList.remove('selected'));
      const target = document.querySelector(link.getAttribute('href'));
      target.classList.add('active');
      link.classList.add('selected');
    });
  });
  if (links.length) links[0].click();
</script>


<br>
<details>
  <summary>
    <span style="font-size:1.25em; font-weight:600;">
      Figure 1. A scatter plot between scaledRI vs. Temperature (color by culture strains)
    </span>
  </summary>
  {% include_relative /html_figures/scaledRI_vs_Temperature.html %}
  <br>
  <br>
  <details>
    <summary>Show Python example</summary>
<pre><code class="language-python">
def get_posteriors(data_dict, stan_file_name):
    from cmdstanpy import CmdStanModel
    # … rest of your function …
</code></pre>
  </details>
</details>

<details>
  <summary>
    <span style="font-size:1.25em; font-weight:600;">
    Figure 2. A dashboard of posterior distributions of culRI-Bayesian models
    </span>
  </summary>
  {% include_relative /html_figures/Bayesians_hyperparams.html %}

  <br>
  <details>
    <summary>
      <span style="font-size:1.25em; font-weight:600;">
      RI residuals of culRI-Bayesian models
      </span>
    </summary>
    {% include_relative /html_figures/Bayesians_hyperparams_residuals.html %}
  </details>
</details>

<details>
  <summary>
    <span style="font-size:1.25em; font-weight:600;">
    Figure 3. Paleo-showcases
    </span>
  </summary>

  <br>
  <br>
  <details>
    <summary>
      <span style="font-size:1.25em; font-weight:600;">
      3.1 PETM showcase
      </span>
    </summary>
  {% include_relative /html_figures/WilsonLakePETM_showcase.html %}
  </details>

  <br>
  <br>
  <details>
    <summary>
      <span style="font-size:1.25em; font-weight:600;">
      3.2 Glacial-Interglacial showcase
      </span>
    </summary>
  {% include_relative /html_figures/MD98-2152_G-IG_showcase.html %}
  </details>
</details>