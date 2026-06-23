# can you guess which system necessitated writing this script? (hint: it rhymes with scarepoint!)
# analyses a directory for paths longer than a specified length. if it finds any, it gives you the option to rename the file,
# or any of the folders that it sits in.
# I wrote this script while running on four hours of sleep. please forgive me. however much you might hate this code, I hate it more :D

import json
import os
import subprocess
import sys
import textwrap

try:
    source_dir = sys.argv[1]
    max_path_length = int(sys.argv[2])
except IndexError:
    print("Please provide the source directory and the maximum path length.")

number_of_long_paths = 0

# some universal adjustments to paths that may make the path just short enough.
easy_wins = {
    " and ": "&",
    " - ": "-",
    "( ": "(",
    " )": ")",
    "  ": " ",
    " .": ".",
    ", ": ",",
    "..": ".",
    "certificate": "cert",
    "Certificate": "Cert",
    "CERTIFICATE": "CERT",
    "Applications": "Apps",
    "Assessment": "Assmnt",
}
try:
    with open("folder_renames.json", "r") as f:
        folder_renames = json.load(f)
except:
    folder_renames = {}

print(folder_renames)


# the check pass - this finds any offending file_names/folders
try:
    for root, dirs, file_names in os.walk(source_dir):
        for file_name in file_names:
            full_path = os.path.join(root, file_name)
            # remove the root part of the path - we only want to know the length of the path from the folder the user specifies
            source_dir_last = source_dir.split("/")[-1]
            split_path = full_path.split(source_dir_last)[-1]
            local_path = "".join([source_dir_last, split_path])

            if len(local_path) > max_path_length:
                print(f"The file '{file_name}' has too long of a path!")
                print(
                    textwrap.dedent(f"""
                    Full path:
                    {local_path}
                    Path length: {len(local_path)}
                    """)
                )
                print("Attempting easy wins...")
                for easy_win in easy_wins:
                    if easy_win in local_path:
                        local_path = local_path.replace(easy_win, easy_wins[easy_win])
                print("Attemping known folder renames...")
                for folder in folder_renames:
                    if folder in local_path:
                        local_path = local_path.replace(folder, folder_renames[folder])
                print(
                    textwrap.dedent(f"""
                    Path updated to:
                    {local_path}
                    New path length:
                    {len(local_path)}
                    """)
                )
                if len(local_path) < max_path_length:
                    print("Path sufficiently shortened.")
                    print("=" * max_path_length)
                else:
                    while len(local_path) > max_path_length:
                        print(
                            f"""
                            Path still {len(local_path) - max_path_length} chars too long.
                            Current path: {local_path}
                            Biggest offending folders:
                            """
                        )
                        # we want to get each folder individually, so that the user can see which are the biggest culprits (i.e. have the longest names).
                        folders_in_path = {}
                        for index, folder in enumerate(local_path.split("/")[0:-1]):
                            folders_in_path[folder] = local_path.split("/")[:index]
                        sorted_folders_in_path = sorted(
                            folders_in_path.keys(),
                            key=lambda folder: len(folder),
                            reverse=True,
                        )
                        for index, folder in enumerate(sorted_folders_in_path):
                            print(f"{index + 1}: {folder}")
                        print(
                            "Type 'f' followed by the folder number to rename the folder. Type 'r' to rename the file. Type 'o' followed by the folder number to view it in finder."
                        )
                        selection = input("Selection: ")
                        if "f" in selection:
                            folder_to_rename = int(selection[1:]) - 1
                            new_folder_name = input(
                                "Enter the new name for the folder: "
                            )
                            folder_renames[sorted_folders_in_path[folder_to_rename]] = (
                                new_folder_name
                            )
                            local_path = local_path.replace(
                                sorted_folders_in_path[folder_to_rename],
                                new_folder_name,
                            )
                        elif "r" in selection:
                            new_file_name = input(
                                "Enter the new name for the file_name: "
                            )
                            local_path = local_path.replace(file_name, new_file_name)
                        elif "o" in selection:
                            folder_to_open = sorted_folders_in_path[
                                int(selection[1:]) - 1
                            ]
                            # we may have already renamed the folder. let's find the original folder name.
                            for old_name, new_name in folder_renames.items():
                                if new_name == folder_to_open:
                                    folder_to_open = old_name
                            folder_path = (
                                full_path.split(folder_to_open)[0] + folder_to_open
                            )
                            print(folder_path)
                            subprocess.run(["open", folder_path])
                    print("Path sufficiently shortened.")
                    print("=" * max_path_length)

                number_of_long_paths += 1
except KeyboardInterrupt:
    print("Saving folder renames...")
    with open("folder_renames.json", "w+") as f:
        json.dump(folder_renames, f, ensure_ascii=False, indent=4)
    exit(0)

if number_of_long_paths > 0:
    # time for the main event - let's rename ALL the files and folders based off the previous loop.
    for root, dirs, file_names in os.walk(source_dir):
        for file_name in file_names:
            full_path = os.path.join(root, file_name)
            new_path = full_path
            for easy_win in easy_wins:
                if easy_win in new_path:
                    new_path = new_path.replace(easy_win, easy_wins[easy_win])
            for folder in folder_renames:
                if folder in new_path:
                    new_path = new_path.replace(folder, folder_renames[folder])
            print(f"Renaming {full_path} to {new_path}")
