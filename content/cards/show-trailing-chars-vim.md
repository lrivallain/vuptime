---
layout: card
title: Highlight unwanted chars in vim editor
author: lrivallain
tags:
- linux
- vim
date: 2018-08-22
---

Source: [vim.wikia.com](http://vim.wikia.com/wiki/Highlight_unwanted_spaces)

Show all tabs:

```
/\t
```

Show trailing whitespace:

```
/\s\+$
```

Show trailing whitespace only after some text (ignores blank lines):

```
/\S\zs\s\+$
```

Show spaces before a tab:

```
/ \+\ze\t
```

