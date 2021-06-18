import os, sys
import argparse


parser = argparse.ArgumentParser(description='Rewrite tags in yaml list')
parser.add_argument('filename')
args = parser.parse_args()
with open(args.filename) as i_file:
    new_file_content = ""
    for line in i_file.readlines():
        if line.startswith("tags:"):
            tags = line.replace('tags:', '').lstrip().split(' ')
            n_line = "tags:\n"
            for tag in tags:
                if tag != "":
                    n_line += "- " + tag + '\n'
            new_file_content += n_line.replace('\n\n', '\n')
        else:
            new_file_content += line
#    print(new_file_content)

with open(args.filename, 'w') as o_file:
    o_file.write(new_file_content)
