import sys
from pathlib import Path

try:
    source_dir = Path(sys.argv[1])
    max_path_length = int(sys.argv[2])
except IndexError:
    print("Please provide the source directory and the maximum path length.")
    exit(1)


def calculate_path_length(file: Path, source_dir: Path):
    return len(get_relative_path(file, source_dir))


# returns a string of the full path, minus the directories above source_dir
def get_relative_path(path: Path, source_dir: Path):
    return str(path.relative_to(source_dir.parent))


number_of_long_paths = 0

for current_dir, dir_name, files in source_dir.walk():
    for file_name in files:
        file_path = current_dir / file_name
        if calculate_path_length(file_path, source_dir) > max_path_length:
            difference_in_length = (
                calculate_path_length(file_path, source_dir) - max_path_length
            )
            print(
                file_path.resolve(),
                f"is {difference_in_length} chars longer than maximum.",
            )
            number_of_long_paths += 1

print(f"Total long paths: {number_of_long_paths}")
