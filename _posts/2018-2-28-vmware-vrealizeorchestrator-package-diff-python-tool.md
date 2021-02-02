---
layout: post
title: VMware vRealize orchestrator package diff python tool
category: VMware
author: lrivallain
tags: vmware orchestrator vrealize python diff script
---

I have recently published a draft tool to provide a table-formated diff of two vRealize Orchestrator packages.

Project is available on [GitHub project](https://github.com/lrivallain/vro-package-diff/) and will evolve in futur to support more package item's types and to provide better information about differences.

{% include lightbox.html src="/images/vro-diff-package/vro-package-diff-sample.png" title="Sample of output" %}

## Installation

**Requirements:** Python 3 and `pip` installed.

Download:
```bash
git clone https://github.com/lrivallain/vro-package-diff.git
cd vro-package-diff
```

 (optionnal) Create python virtualenv:
```bash
virtualenv -p python3 --no-site-packages venv
. venv/bin/activate
```

Install required python packages:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python ./vro_package_diff.py packageA.package packageB.package
```
With:
* `packageA.package` : oldest package file
* `packageB.package` : newest package file

## Logs

Execution logs are saved in the `diff.log` file. The file is overwritten at each execution of the diff tool.
