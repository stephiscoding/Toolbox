# randomise-file-names.py
# takes a directory of files, and randomises the names of them

import os
import sys
import random

try:
    source_dir = sys.argv[1]
except IndexError:
    print("Please specify a directory.")
    exit()

for root, dirs, files in os.walk(source_dir):
    for file in files:
        full_path = os.path.join(root, file)
        extension = file.split('.')[1]
        renamed_path = os.path.join(root, f"{random.randrange(100000,999999)}.{extension}")
        print(f"Renaming {full_path} to {renamed_path}")
        os.rename(full_path, renamed_path)

