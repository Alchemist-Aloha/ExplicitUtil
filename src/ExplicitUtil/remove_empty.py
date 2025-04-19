import os
import logging
__docformat__ = "google"

def remove_empty_folders(root_dir:str, dry_run:bool=False) -> int:
    """
    Recursively removes empty folders starting from the deepest level
    
    Args:
        root_dir (str): Path to the directory to clean
        dry_run (bool): If True, only report what would be removed without actually removing
    
    Returns:
        int: Number of directories removed
    """
    if not os.path.isdir(root_dir):
        print(f"'{root_dir}' is not a valid directory")
        return 0
    
    print(f"Scanning for empty directories in: {root_dir}")
    
    count = 0
    # Walk bottom-up so we handle the deepest directories first
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Skip the root directory itself
        if dirpath == root_dir:
            continue
        
        # Check if this directory is empty (no files and no non-empty subdirectories)
        if not filenames and not dirnames:
            if dry_run:
                print(f"Would remove empty directory: {dirpath}")
            else:
                try:
                    os.rmdir(dirpath)
                    print(f"Removed empty directory: {dirpath}")
                    count += 1
                except OSError as e:
                    print(f"Failed to remove directory '{dirpath}': {e}")
    
    action = "Would remove" if dry_run else "Removed"
    print(f"{action} {count} empty directories")
    return count

def main() -> None:
    target_dir = input("Please enter the target directory: ").strip("\"")
    dry_run = input("Do you want to perform a dry run? (y/n): ").strip().lower() == 'y'
    
    target_path = os.path.abspath(target_dir)
    if not os.path.exists(target_path):
        print(f"Directory does not exist: {target_path}")
        exit(1)
    
    remove_empty_folders(target_path, dry_run)
    return

if __name__ == "__main__":
    main()