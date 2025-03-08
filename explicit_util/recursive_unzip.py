# -*- coding: utf-8 -*-
import zipfile
import argparse
from pathlib import Path

def recursive_unzip(folder_path: str, delete_zips: bool = False) -> None:
    """
    Unzips each ZIP archive in a folder and its subfolders into a separate folder
    named after the archive.

    Args:
        folder_path (str or Path): The path to the folder containing ZIP archives.
        delete_zips (bool, optional): Whether to delete the ZIP archives after unzipping. Defaults to False.
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    folder = Path(folder_path)
    
    for zip_path in folder.glob('**/*.zip'):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Create a folder with the same name as the ZIP file (without the .zip extension)
                extract_path = zip_path.parents[0]
                                
                zip_ref.extractall(extract_path)
            print(f"Unzipped: {zip_path} to {extract_path}")
            
            if delete_zips:
                zip_path.unlink()
                print(f"Deleted: {zip_path}")
        except zipfile.BadZipFile:
            print(f"Error: {zip_path} is not a valid ZIP file.")
        except Exception as e:
            print(f"An error occurred while processing {zip_path}: {e}")
                    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unzip ZIP archives into folders named after the archives.")
    parser.add_argument("folder", help="The folder to process.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete ZIP archives after unzipping.")

    args = parser.parse_args()
    folder = Path(args.folder)

    if not folder.exists():
        print(f"Error: Folder '{folder}' does not exist.")
        exit(1)

    recursive_unzip(folder, args.delete)