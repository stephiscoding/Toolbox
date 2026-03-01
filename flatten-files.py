# flatten-files.py
# takes a directory containing files that may be in subdirectories, and then moves the files to a second directory, flattening the directory structure.

import os
import sys

try:
    source_dir = sys.argv[1]
    dest_dir = sys.argv[2]
except IndexError:
    print("Please specify a source and destination directory.")
    exit()

files_to_move = []

for root, dirs, files in os.walk(source_dir):
    for file in files:
        full_path = os.path.join(root, file)
        dest_path = os.path.join(dest_dir, file)
        print(f"Moving {full_path} to {dest_path}")
        os.rename(full_path, dest_path)

