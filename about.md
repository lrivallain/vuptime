---
layout: about
title: About
---

This blog is maintained by [**Ludovic Rivallain**](#lrivallain) but also hosts contributions from {% comment %}[**Jérémy Rossignol**](#jrossignol) and {% endcomment %}[**Antoine Harlaut**](#aharlaut).

{% for author in site.data.authors %}
<div class="card" id="{{ author.nick }}">
    <div class="card-header">
        {{ author.display_name }}
    </div>
    <div class="card-block">
        {% capture author_include %}{% include {{ author.nick }}.md %}{% endcapture %}
        {{ author_include | markdownify }}
    </div>
    <div class="card-footer">
      {% if author.blog %}    
        <a href="{{ author.blog }}" title="Visit blog"><i class="svg-icon blog"></i></a>
      {% endif %}
      {% if author.linkedin %}
        <a href="https://www.linkedin.com/in/{{ author.linkedin }}" title="Visit Linkedin profile"><i class="svg-icon linkedin"></i></a>
      {% endif %}
      {% if author.twitter %}
        <a href="https://www.twitter.com/{{ author.twitter }}" title="Visit Twitter profile"><i class="svg-icon twitter"> </i></a>
      {% endif %}
      {% if author.github %}
        <a href="https://github.com/{{ author.github }}" title="Visit Github profile"><i class="svg-icon github">  </i></a>
      {% endif %}
    </div>
</div>
{% endfor %}
<div class="card" id="copyright">
  <div class="card-header">
    © 2014 - 2021 – Copyright notice
  </div>
  <div class="card-block">
      <p>Except where otherwise noted, all data and written content are licensed under the <a href="https://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)</a>.</p>
      <p><b>Exclusions</b>: Some illustrations and commercial logos are and remains the entire property of the respective publishers and cannot be considered under the CC BY-NC 4.0 license.</p>
      <p>This website is powered-by <a href="https://jekyllrb.com/">Jekyll</a> and the <a href="https://github.com/dlinsley/jekyll-clarity">jekyll-clarity</a> theme.</p>
  </div>
</div>

[Status page 📈](https://stats.uptimerobot.com/K1DpTO1N)
