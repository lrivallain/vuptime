---
layout: post
title: New release of VMware vRealize Orchestrator package diff tool
category: VMware
author: lrivallain
tags: vmware orchestrator vrealize python diff script
---

About a year ago, I published a small tool to compare two VMware vRealize Orchestrator packages file: [vRO Package Diff](/2018/02/28/vmware-vrealizeorchestrator-package-diff-python-tool/). Initial version was a simple python script accepting 2 files as arguments and without any input controls.

Today, I publish a v2 of the tool with the following changes:

- `vro-package-diff` is now a Pypi hosted project: [vro-package-diff](https://pypi.org/project/vro-package-diff/) and so, can be installed with `pip install` command.
- An endpoit `vro-diff` to access to the tool from any path location.
- Usage of [`click`](https://click.palletsprojects.com/) to manage:
  - inputs packages
  - help
  - legend display
  - test feature
- A *test* feature
- Documentation is hosted on [vro-package-diff.readthedocs.io](https://vro-package-diff.readthedocs.io)
- [Travis pipeline](https://travis-ci.org/lrivallain/vro-package-diff/)

![Sample output of vro-diff-package](/images/vro-diff-package/vro-diff-package_v2.png)

## Install the new version

From a python environment with `pip` installed:

```bash
pip install vro-package-diff
```

## Usage

### Get the help

```bash
vro-diff --help
Usage: vro-diff [OPTIONS] REFERENCE_PACKAGE COMPARED_PACKAGE

Start a diff operation between two vRO packages.

REFERENCE_PACKAGE is the package you want to use as source
COMPARED_PACKAGE is the one you want to compare with reference one

Options:
-l, --legend  Display the legend after the diff table
-t, --test    Exit with `0` if package can be safely imported. Else, returns
                the number of errors
-h, --help    Show this message and exit.
```

### Examples

Compare two packages:

```bash
vro-diff tests/data/package_v1.0.package tests/data/package_v1.1.package
```

Compare, then display legend (`--legend`):

```bash
vro-diff --legend --test tests/data/package_v1.0.package tests/data/package_v1.1.package
```

Compare, then exit with error if there is conflicts (`-–test`):

```bash
vro-diff --test tests/data/package_v1.0.package tests/data/package_v1.1.package
echo $?
```

The script will exit with the number of items with a conflict situation.

This `-–test` option can be usefull to implement CI/CD pipelines to compare, then upload(if there is no conflict) vRO packages.

### Contributions

This tool needs vRO users to be tested and improved based on feedback and [contributions](https://github.com/lrivallain/vro-package-diff/graphs/contributors): Feel free to [open issue](https://github.com/lrivallain/vro-package-diff/issues/new) or [create pull request](https://github.com/lrivallain/vro-package-diff/compare).