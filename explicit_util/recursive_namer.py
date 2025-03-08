from pathlib import Path
import subprocess


def process_video_files(root_dir:str, namer_config:str=".namer.cfg", suffix:tuple[str]=(".m4v", ".mp4"),endswith:tuple[str]=("")) -> None: 
    """
    Recursively finds and processes .m4v and .mp4 files in subfolders of root_dir.

    Args:
        root_dir (str): The starting directory.
        namer_config (str): Path to the namer configuration file.
        suffix (tuple): Tuple of file extensions to process.
        endswith (tuple): Tuple of suffixes to check for in the file name.
    """
    root_dir = Path(root_dir)  # Ensure root_dir is a Path object
    if not root_dir.exists():
        print(f"Error: Directory '{root_dir}' not found.")
        return

    for item in root_dir.rglob("*"):  # Use rglob to recursively find all files
        if (
            item.is_file()
            and (item.suffix.lower() in suffix)
            and str(item.stem).lower().endswith(endswith)
        ):
            print(f"Processing file: {item}")
            run_namer_command(item, namer_config)  # process the parent directory.


def run_namer_command(directory:Path, namer_config:str=".namer.cfg") -> tuple[str, str, int]:
    """
    Executes a PowerShell command to process files in a directory.
    Try fetch from jellyfin generated nfo first. If fails, try to rename using theporndb.net.
    
    Args:
        directory (Path): The directory to process.
        namer_config (str): Path to the namer configuration file.

    Returns:
        tuple: A tuple containing (stdout, stderr, returncode).
    """
    try:
        command = (
            f'python -m namer rename -c "{namer_config}" -f "{str(directory)}" -i -v'
        )
        process = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            check=False,
        )
        stdout = process.stdout
        stderr = process.stderr
        returncode = process.returncode
        print(stdout)
        # print(stderr)
        print(returncode)
        if returncode == 0:
            print(f"Error processing {directory}: {stderr}")
            command = (
                f'python -m namer rename -c "{namer_config}" -f "{str(directory)}" -v'
            )
            process = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                check=False,
            )
            print(process.stdout)
        return stdout, stderr, returncode
    except Exception as e:
        return None, str(e), -1



def get_leaf_directories(root_path:Path) -> list[Path]:
    """
    Recursively finds all directories within root_path that contain no further subdirectories.

    Args:
        root_path (Path): The starting directory.

    Returns:
        list: A list of Path objects representing the leaf directories.
    """
    leaf_dirs = []
    if not root_path.is_dir():
        return leaf_dirs

    for item in root_path.iterdir():
        if item.is_dir():
            if not any(sub_item.is_dir() for sub_item in item.iterdir()):
                # If no sub-directories are found, it's a leaf directory.
                leaf_dirs.append(item)
            else:
                # Recursively check subdirectories.
                leaf_dirs.extend(get_leaf_directories(item))
    return leaf_dirs

def process_leaf_files(root_dir:Path, namer_config:str=".namer.cfg") -> None:
    """
    Processes leaf directories in root_dir using the specified namer configuration.

    Args:
        root_dir (Path): The starting directory.
        namer_config (str): Path to the namer configuration file.
    """
    leaf_directories = get_leaf_directories(root_dir)
    for directory in leaf_directories:
        print(directory)
        stdout, stderr, returncode = run_namer_command(directory, namer_config)
        if returncode == 0:
            print("PowerShell command output:")
            print(stdout)
        else:
            print("PowerShell command error:")
            print(stderr)
            print(f"Return code: {returncode}")
    
    
if __name__ == "__main__":
    # Example Usage
    ROOT_DIR = Path(input("Enter the folder path to video files: ")) #replace with your directory.
    if not ROOT_DIR.is_dir():
        print(f"Error: Directory '{ROOT_DIR}' not found.")
        exit(1)
    NAMER_CONFIG = ".namer.cfg"
    if not Path(NAMER_CONFIG).is_file():
        print(f"Error: Configuration file '{NAMER_CONFIG}' not found.")
        exit(1)
    process_video_files(ROOT_DIR, NAMER_CONFIG, suffix=[".m4v", ".mp4"],endswith=(""))
