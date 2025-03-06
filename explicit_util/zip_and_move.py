# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import zipfile
import hashlib

def is_leaf_directory(folder: Path) -> bool:
    """Check if a directory is a leaf directory (has no subdirectories) and is non-empty.
    Args:
        folder (Path): The directory to check.
        
    Returns:
        bool: True if the directory is a leaf directory, False otherwise.
    """
    return (
        folder.is_dir()
        and any(folder.iterdir())
        and not any(p.is_dir() for p in folder.iterdir())
    )

def zip_directory(folder: Path, zip_path: Path) -> None:
    """Create a zip archive of the given folder.
    Args:
        folder (Path): The directory to zip.
        zip_path (Path): The path where the zip file will be saved.
    """
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in folder.rglob("*"):  # Recursively get all files
            if file.is_file():  # Only include files, not directories
                zipf.write(file, file.relative_to(folder.parent))

def compute_checksum(file_path: Path) -> str:
    """Compute the SHA-256 checksum of a file.
    Args:
        file_path (Path): The path to the file.
    Returns:
        str: The SHA-256 checksum of the file.
    """
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def zip_and_move(source_folder:Path, destination_folder:Path) -> None:
    """Zip leaf directories and move them to the destination folder.
    Args:
        source_folder (Path): The source directory containing folders to zip.
        destination_folder (Path): The destination directory where zipped folders will be moved.
    """
    for folder in source_folder.rglob("*"):
        if is_leaf_directory(folder):
            # Create relative path for preserving structure
            relative_path = folder.relative_to(source_folder)
            zip_name = f"{folder.name}.zip"

            # Create destination path maintaining original structure
            dest_path = destination_folder / relative_path.parent
            dest_path.mkdir(parents=True, exist_ok=True)

            # Zip and move
            zip_path = dest_path / zip_name
            temp_zip_path = folder.parents[0] / f"{folder.name}_temp.zip"
            zip_directory(folder, temp_zip_path)

            if zip_path.exists():
                existing_checksum = compute_checksum(zip_path)
                new_checksum = compute_checksum(temp_zip_path)
                if existing_checksum == new_checksum:
                    print(f"Skipping {zip_path} as it already exists and matches the checksum.")
                    temp_zip_path.unlink()  # Remove temporary zip file
            else:
                print(f"Moving {folder} to {dest_path}")
                shutil.move(temp_zip_path, zip_path)

if __name__ == "__main__":
    source_folder = Path(input("Enter the source folder path: "))
    if not source_folder.is_dir():
        print(f"The folder '{source_folder}' does not exist.")
        exit(1)
    destination_folder = Path(input("Enter the destination folder path: "))
    if not destination_folder.is_dir():
        print(f"The folder '{destination_folder}' does not exist.")
        exit(1)
    zip_and_move(source_folder, destination_folder)
