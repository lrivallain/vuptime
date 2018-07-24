#!/usr/bin/env bash
export LANG=en_US.UTF-8
python3 tag_generator.py
jekyll serve --config _config.yml -H 0.0.0.0 --incremental
