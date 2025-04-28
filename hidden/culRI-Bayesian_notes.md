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

<br>
<br>
## **Logistic functional forms**
<iframe
  src="/assets/html/logistic_fixed_upper_interactive.html"
  width="100%"
  height="600"
  frameborder="0"
></iframe>

<br>
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

<br>
<br>
<details>
  <summary>
    <span style="font-size:1.25em; font-weight:600;">
    Figure 2. A dashboard of posterior distributions of culRI-Bayesian models
    </span>
  </summary>
  {% include_relative /html_figures/Bayesians_hyperparams.html %}

  <br>
  <br>
  <details>
    <summary>
      <span style="font-size:1.25em; font-weight:600;">
      RI residuals of culRI-Bayesian models
      </span>
    </summary>
    {% include_relative /html_figures/Bayesians_hyperparams_residuals.html %}
  </details>

<!-- Make a window to view all stan files dynamically -->

{% comment %}
  Grab every static file whose path contains '/hidden/stan_files/'
  (we assume you only put .stan files in there)
{% endcomment %}
{% assign stanfiles = site.static_files 
   | where_exp: "f", "f.path contains '/hidden/stan_files/'" %}
<br>
<br>
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
</details>

<br>
<br>
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