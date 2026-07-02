# can you guess which system necessitated writing this script? (hint: it rhymes with scarepoint!)
# analyses a directory for paths longer than a specified length. if it finds any, it gives you the option to rename the file,
# or any of the folders that it sits in.

import json
import os
import readline
import subprocess
import sys
import textwrap
from pathlib import Path

import pyperclip

try:
    source_dir = Path(sys.argv[1])
    max_path_length = int(sys.argv[2])
except IndexError:
    print("Please provide the source directory and the maximum path length.")
    exit(1)

# some universal adjustments to paths that may make the path just short enough.
easy_wins = {
    " and ": "&",
    " & ": "&",
    " - ": "-",
    "( ": "(",
    " )": ")",
    "  ": " ",
    " .": ".",
    ", ": ",",
    "..": ".",
    "certificate ii ": "cert2 ",
    "Certificate II ": "Cert2 ",
    "CERTIFICATE II ": "CERT2 ",
    "certificate iii ": "cert2 ",
    "Certificate III ": "Cert3 ",
    "CERTIFICATE III ": "CERT3 ",
    "certificate iv ": "cert4 ",
    "Certificate IV ": "Cert4 ",
    "CERTIFICATE IV ": "CERT4 ",
    "Certificate": "Cert",
    "certificate": "cert",
    "CERTIFICATE": "CERT",
    "CERT II ": "CERT2 ",
    "CERT III ": "CERT3 ",
    "Applications": "Apps",
    "Assessment": "Assmnt",
    "assessment": "assmnt",
    "Version ": "V",
    "version ": "V",
    "Service": "Srvc",
    "service": "srvc",
    "Information": "Info",
    "information": "info",
}


def load_json_dict(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        print(f"Warning: {filename} not found. Starting fresh.")
        return {}


def load_json_set(filename):
    try:
        with open(filename, "r") as f:
            return set(json.load(f))
    except:
        print(f"Warning: {filename} not found. Starting fresh.")
        return set([])


folder_renames = load_json_dict("folder_renames.json")
file_renames = load_json_dict("file_renames.json")
files_to_delete = load_json_set("files_to_delete.json")


def calculate_path_length(file: Path, source_dir: Path):
    return len(get_relative_path(file, source_dir))


# returns a string of the full path, minus the directories above source_dir
def get_relative_path(path: Path, source_dir: Path):
    return str(path.relative_to(source_dir.parent))


def apply_known_renames(effective_path: str) -> str:
    """Applies easy wins and known folder renames to a path string."""
    # Note: Since the rename maps (easy_wins, folder_renames) are string-based
    # and replacements can cascade or introduce errors, this must remain a string operation.
    path = effective_path

    # Apply easy wins
    for easy_win, replacement in easy_wins.items():
        if easy_win in path:
            path = path.replace(easy_win, replacement)

    # Apply known folder renames
    for folder, new_name in folder_renames.items():
        if folder in path:
            path = path.replace(folder, new_name)

    # Apply known file renames
    for file, new_name in file_renames.items():
        if file in path:
            path = path.replace(file, new_name)
    return path


done = 0
try:
    for current_dir, dir_name, files in source_dir.walk():
        for file_name in files:
            done += 1
            file_path = current_dir / file_name
            if (
                calculate_path_length(file_path, source_dir) > max_path_length
                and get_relative_path(file_path, source_dir) not in files_to_delete
            ):
                effective_path = get_relative_path(file_path, source_dir)
                original_path = effective_path
                print(f"The file '{file_name}' has too long of a path!")
                print(
                    textwrap.dedent(f"""
                    Full path:
                    {effective_path}
                    Path length: {len(effective_path)}
                    """)
                )
                print("Attempting easy wins and applying known renames...")
                effective_path = apply_known_renames(effective_path)
                print(
                    textwrap.dedent(f"""
                    Path updated to:
                    {effective_path}
                    New path length:
                    {len(effective_path)}
                    """)
                )
                while (
                    len(effective_path) > max_path_length
                    and get_relative_path(file_path, source_dir) not in files_to_delete
                ):
                    print(
                        textwrap.dedent(f"""
                        Path still {len(effective_path) - max_path_length} chars too long.
                        Current path: {effective_path}
                        Biggest offending folders:
                        """)
                    )
                    # we want to get each folder individually, so that the user can see which are the biggest culprits (i.e. have the longest names).
                    folders_in_path = Path(effective_path).parent.parts
                    sorted_folders_in_path = sorted(
                        folders_in_path,
                        key=lambda folder: len(folder),
                        reverse=True,
                    )
                    for index, folder in enumerate(sorted_folders_in_path):
                        print(f"{index + 1}: {folder}", end="")
                        if folder in folder_renames.values():
                            print(" -> already renamed")
                        else:
                            print()
                    # get the current file name
                    file_name = Path(effective_path).name
                    print(
                        "Type 'f' followed by the folder number to rename the folder. Type 'r' to rename the file. Type 'd' to delete the file. Type 'o' followed by the folder number to view it in finder."
                    )
                    selection = input("Selection: ")
                    if "f" in selection:
                        folder_to_rename = int(selection[1:]) - 1
                        original_folder_name = sorted_folders_in_path[folder_to_rename]
                        pyperclip.copy(original_folder_name)
                        new_folder_name = input(
                            f"New name for {original_folder_name}: "
                        )
                        folder_renames[original_folder_name] = new_folder_name
                        effective_path = effective_path.replace(
                            original_folder_name,
                            new_folder_name,
                        )
                    elif "r" in selection:
                        pyperclip.copy(file_name)
                        new_file_name = input("Enter the new name for the file: ")
                        file_renames[file_name] = new_file_name
                        effective_path = effective_path.replace(
                            file_name, new_file_name
                        )
                    elif "o" in selection:
                        folder_to_open = sorted_folders_in_path[int(selection[1:]) - 1]
                        # we may have already renamed the folder. let's find the original folder name.
                        for old_name, new_name in folder_renames.items():
                            if new_name == folder_to_open:
                                folder_to_open = old_name
                        folder_path = source_dir.resolve().parent / Path(
                            original_path.split(folder_to_open)[0] + folder_to_open
                        )
                        print(folder_path)
                        subprocess.run(["open", folder_path])
                    elif "d" in selection:
                        files_to_delete.add(get_relative_path(file_path, source_dir))
                print(f"Path sufficiently shortened. Completed: {done}")
                print("=" * max_path_length)
                print("\nExecuting renames...")

    input(
        "Ready to begin filesystem modification. Press Enter to continue, or Ctrl-C to exit..."
    )
    # 1. Easy Wins (Applying to the actual files/folders on disk)
    easy_tasks = []
    try:
        for p in source_dir.rglob("*"):
            old_name = p.name
            new_name = old_name
            for easy_win, replacement in easy_wins.items():
                if easy_win in new_name:
                    new_name = new_name.replace(easy_win, replacement)
            if new_name != old_name:
                easy_tasks.append((p, new_name))
    except Exception as e:
        print(f"Error during easy wins collection: {e}")

    # Execute easy wins depth-first (children before parents)
    easy_tasks.sort(key=lambda x: len(x[0].parts), reverse=True)
    for p, new_name in easy_tasks:
        if p.exists():
            try:
                print(f"Applying easy win: {p.name} -> {new_name}")
                p.rename(p.with_name(new_name))
            except Exception as e:
                print(f"Error applying easy win to {p}: {e}")

    # 2. File Renames
    for old_name, new_name in file_renames.items():
        try:
            for p in source_dir.rglob(old_name):
                if p.is_file() and p.name == old_name:
                    print(f"Renaming file: {p.name} -> {new_name}")
                    p.rename(p.with_name(new_name))
        except Exception as e:
            print(f"Error renaming files matching '{old_name}': {e}")

    # 3. Folder Renames (Depth-First)
    folder_tasks = []
    for old_name, new_name in folder_renames.items():
        try:
            for p in source_dir.rglob(old_name):
                if p.is_dir() and p.name == old_name:
                    folder_tasks.append((p, new_name))
        except Exception as e:
            print(f"Error collecting folder renames for '{old_name}': {e}")

    # Sort depth-first (deepest first) to prevent breaking paths
    folder_tasks.sort(key=lambda x: len(x[0].parts), reverse=True)
    for p, new_name in folder_tasks:
        if p.exists():
            try:
                print(f"Renaming folder: {p.name} -> {new_name}")
                p.rename(p.with_name(new_name))
            except Exception as e:
                print(f"Error renaming folder {p}: {e}")

    # 4. Files to Delete
    for rel_path_str in files_to_delete:
        try:
            # Resolve path relative to source_dir
            p = source_dir / rel_path_str
            if p.exists():
                print(f"Deleting file: {rel_path_str}")
                p.unlink()
        except Exception as e:
            print(f"Error deleting {rel_path_str}: {e}")

    print("Renames completed.\n")
finally:
    print("\nSaving renames...")
    with open("folder_renames.json", "w+") as f:
        json.dump(folder_renames, f, ensure_ascii=False, indent=4)
    with open("file_renames.json", "w+") as f:
        json.dump(file_renames, f, ensure_ascii=False, indent=4)
    with open("files_to_delete.json", "w+") as f:
        json.dump(list(files_to_delete), f, ensure_ascii=False, indent=4)
    exit(0)
