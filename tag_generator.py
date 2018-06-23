#!/usr/bin/env python3

'''
tag_generator.py
Copyright 2017 Long Qian
Contact: lqian8@jhu.edu
This script creates tags for your Jekyll blog hosted by Github page.
No plugins required.
'''

import glob
import os
import re
import shutil
from tempfile import mkstemp


def sed(pattern, replace, source, dest=None, count=0):
    """Reads a source file and writes the destination file.
    In each line, replaces pattern with replace.

    source: https://stackoverflow.com/a/40843600

    Args:
        pattern (str): pattern to match (can be re.pattern)
        replace (str): replacement str
        source  (str): input filename
        count (int): number of occurrences to replace
        dest (str):   destination filename, if not given, source will be over written.
    """

    fin = open(source, 'r')
    num_replaced = count

    if dest:
        fout = open(dest, 'w')
    else:
        fd, name = mkstemp()
        fout = open(name, 'w')

    for line in fin:
        out = re.sub(pattern, replace, line)
        fout.write(out)

        if out != line:
            num_replaced += 1
        if count and num_replaced > count:
            break
    try:
        fout.writelines(fin.readlines())
    except Exception as E:
        raise E

    fin.close()
    fout.close()

    if not dest:
        shutil.move(name, source)


def generate_tags(post_dir,tag_dir,layout):
    os.makedirs(tag_dir, exist_ok=True)
    filenames = glob.glob(post_dir + '*md')

    total_tags = []
    for filename in filenames:
        f = open(filename, 'r', encoding="utf8")
        crawl = False
        for line in f:
            if crawl:
                current_tags = line.strip().split()
                if current_tags[0] == 'tags:':
                    total_tags.extend(current_tags[1:])
                    crawl = False
                    break
            if line.strip() == '---':
                if not crawl:
                    crawl = True
                else:
                    crawl = False
                    break
        f.close()
    total_tags = set(total_tags)

    old_tags = glob.glob(tag_dir + '*.md')
    for tag in old_tags:
        os.remove(tag)

    for tag in total_tags:
        tag_filename = tag_dir + tag + '.md'
        f = open(tag_filename, 'a')
        write_str = '---\nlayout: '+ layout +'\ntitle: \"Tag: ' + tag + '\"\ntag: ' + tag + '\nrobots: noindex\n---\n'
        f.write(write_str)
        f.close()
    print("Tags generated, count", total_tags.__len__())
    return total_tags


# Generate tag for posts
post_dir = '_posts/'
tag_dir = 'tag/'
layout = 'tagpage'
tags = generate_tags(post_dir,tag_dir,layout)

# Generate tag for cards (collection)
post_dir = '_cards/'
tag_dir = 'cards_tag/'
layout = 'cards'
tags = generate_tags(post_dir,tag_dir,layout)
# generate list of tags
tags_pat = re.compile('tags:.*')
sed(tags_pat, 'tags: %s' % ' '.join(tags), "cards.html", count=1)
