import os, sys
import argparse


parser = argparse.ArgumentParser(description='Add alias based on Jekyll URL in yaml list')
parser.add_argument('filename')
args = parser.parse_args()

filename = os.path.basename(args.filename)
jekyll_uri = "/" + filename[0:4] + "/" + filename[5:7] + "/" + filename[8:10] + "/" + filename[11:]
jekyll_uri = jekyll_uri.replace(".md", "/")
print(jekyll_uri)

with open(args.filename) as i_file:
    new_file_content = ""
    for line in i_file.readlines():
        if line.startswith("title:"):
            new_file_content += line
            new_file_content += "aliases: \n"
            new_file_content += "- " + jekyll_uri + "\n"
        else:
            new_file_content += line
    #print(new_file_content)

with open(args.filename, 'w') as o_file:
    o_file.write(new_file_content)
