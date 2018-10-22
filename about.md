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
        <a href="github.com/{{ author.github }}" title="Visit Github profile"><i class="svg-icon github">  </i></a>
      {% endif %}
    </div>
</div>
{% endfor %}

[Status page 📈](https://status.vuptime.io/)
