from pathlib import Path
import re
import os
import shutil
__docformat__ = "google"


def group_files_by_string(directory: Path|str, regex_pattern: str = r"(\d{4}-\d{2}-\d{2})"):
    """Group files in a directory by a specific string in their name.

    Args:
        directory (Path): The directory to search for files.
        string (str): The string to match in file names.

    Returns:
        dict: A dictionary where the keys are the matched strings and the values are lists of file paths.
    """
    directory = Path(directory)
    grouped_files = {}
    pattern = re.compile(regex_pattern)

    for file_path in directory.glob("*"):
        match = pattern.search(file_path.name)
        if match:
            key = match.group(0)
            if key not in grouped_files:
                grouped_files[key] = []
            grouped_files[key].append(file_path)
    # for key in grouped_files:
    #     os.makedirs(directory / key, exist_ok=True)
    #     print(f"Creating directory: {directory / key}")
    #     for file_path in grouped_files[key]:
    #         new_path = directory / key / file_path.name
    #         shutil.move(file_path, new_path)
    #         print(f"Moved {file_path} to {new_path}")
    return grouped_files

def move_grouped_files(directory: Path|str , grouped_files: dict):
    """Move grouped files to their respective directories.

    Args:
        grouped_files (dict): A dictionary where the keys are the matched strings and the values are lists of file paths.
        directory (Path): The directory to move files into.
    """
    for key, files in grouped_files.items():
        os.makedirs(directory / key, exist_ok=True)
        print(f"Creating directory: {directory / key}")
        for file_path in files:
            new_path = directory / key / file_path.name
            shutil.move(file_path, new_path)
            print(f"Moved {file_path} to {new_path}")

if __name__ == "__main__":
    # Example usage
    directory = Path(input("Enter the directory path: ").strip('"'))
    custom_regex = input("Do you want to use a custom regex pattern? (y/n): ").strip().lower()=='y'
    if custom_regex:
        regex_pattern = input("Enter the regex pattern to match: ").strip('"')
    else:
        regex_pattern = r"(\d{4}-\d{2}-\d{2})"
    grouped_files = group_files_by_string(directory, regex_pattern)
    for key, files in grouped_files.items():
        print(f"{key}: {files}")
    proceed = input("Do you want to move the files to their respective directories? (y/n): ").strip().lower()=='y'
    if proceed:
        move_grouped_files(directory, grouped_files)