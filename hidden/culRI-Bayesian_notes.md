---
layout: default
title: culRI-Bayesian notes
permalink: /hidden/culRI-Bayesian_notes.html
---
<meta name="robots" content="noindex">

<style>
  /* Copy-button flash states */
  .code-display-wrapper button.copy:active i.fa-clipboard,
  .code-display-wrapper button.copy:focus i.fa-clipboard {
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
  }
  pre code {
    font-size: 1.1em;
    line-height: 1.4;
    /* color: #d4d4d4; */
    background: #1e1e1e !important;
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

<!-- This is a hidden page for notes on the Bayesian analysis of the Culmination RI data. -->
<!-- The content is not intended for public viewing. -->

# **Bayesian Analysis Notes**
## Developing the new temperature calibration model using Ring Index.

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
### Figure 2. A dashboard of posterior distributions of culRI-Bayesian models
{% include_relative /html_figures/Bayesians_hyperparams.html %}
