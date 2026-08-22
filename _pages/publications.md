---
permalink: /publications/
title: "Publications"
description: "Full list of publications by Inpyo Song — conference and journal papers on video anomaly detection, object tracking, human pose estimation, and traffic accident anticipation."
author_profile: true
---

{%- assign all_pubs = site.publications | sort: "date" | reverse -%}
{%- assign n_pubs = all_pubs | size -%}

<h1 id="-publications-all">📝 Publications</h1>

<p class="pub-intro">
  {{ n_pubs }} entries in total. You can also find them on
  <a href="{{ site.author.googlescholar }}">Google Scholar</a>{% if site.author.googlescholar %}<span id="gs-summary" hidden></span>{% endif %},
  or download the full <a href="/assets/InpyoSong_Curriculum_Vitae_Jun2026.pdf">CV (PDF)</a>.
  <a href="/#-publications" target="_self">&larr; Back to selected publications</a>
</p>

{% for cat in site.publication_categories %}
  {%- assign items = all_pubs | where: "category", cat.key -%}
  {%- if items.size > 0 %}
<h2 id="{{ cat.key }}">{{ cat.title }} <span class="pub-count">{{ items.size }}</span></h2>
<ol class="pub-list pub-list--numbered">
  {%- for pub in items %}
  {%- include publication-item.html pub=pub %}
  {%- endfor %}
</ol>
  {%- endif -%}
{% endfor %}
