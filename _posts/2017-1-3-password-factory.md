---
layout: post
title: Password factory
category: Bash
tags: script linux security bash
---

A quick tip to easily generate random password from a bash command line.

Add the following lines to your `bashrc` file:

```bash
alias genalphanumpasswd='tr -cd '\''[:alnum:]'\'' < /dev/urandom | fold -w30 | head -n1'
alias genpasswd='tr -cd '\''[:graph:]'\'' < /dev/urandom | fold -w30 | head -n1'
```

Save and source it:

```bash
. ~/.bashrc
```

Then you can use it:

```bash
$ genalphanumpasswd
i?`c8.f{Ba^NXwu^9)VD~dao*?S*Bi
$ genalphanumpasswd
75kDvC3fwJAMPPv2CVdEDwNzvHFAZU
```

The first alias, based on `[:graph:]`, produces passwords made of all printable ascii characters except space.

The second one, based on `[:alnum:]`, produces passwords made of A-Z, a-z, 0-9 characters only. This can be usefull depending on the target application.
