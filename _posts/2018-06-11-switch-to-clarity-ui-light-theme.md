---
layout: post
title: Switch to Clarity UI light theme
author: lrivallain
category: Blog
tags: vmware design clarity css
thumb: /images/clarity-ui/after.png
---

As you could notice (if you don't use an RSS tool to read this blog): there is a new UI theme based on the [Clarity Design System](https://vmware.github.io/clarity/).

To compare before/after:
<link rel="stylesheet" href="/includes/cocoen/cocoen.min.css">
<div class="cocoen">
  <img src="/images/clarity-ui/before.png" alt="Before" title="Before">
  <img src="/images/clarity-ui/after.png"  alt="After"  title="After">
</div>

<script src="/includes/cocoen/cocoen.min.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function(){
    new Cocoen();
  });
</script>

This decision was strongly motivated by the new ***HTML5-powered interface*** of vCSA 6.5 & 6.7. This new VMware vCenter UI is also based (as many of others VMware's products) on this open-source design system initiated by VMware and is very enjoyable to use on a daily basis (especially, with the Dark theme from [@BeryJu](https://github.com/BeryJu/dark-vcenter)!).

**Clraity UI** is a mix of UX guidelines, HTML/CSS framework, and Angular components to build web user interface with responsive features, a moderne look and accessibility best-practices. There is a very good documentation available [to start using it](https://vmware.github.io/clarity/documentation/v0.11/get-started) on your project and it contains reference guides for all available components.

Finally, I whant to thank **[@codyde](https://github.com/codyde)** for his post blog [Redesigning My Blog With ClarityUI](https://www.thehumblelab.com/redesigning-my-blog-with-clarityui/) that deeply help me to proceed the change.
