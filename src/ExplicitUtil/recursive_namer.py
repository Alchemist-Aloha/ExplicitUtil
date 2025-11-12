from pathlib import Path
import subprocess
from typing import Union, Tuple
import platform
import random
import asyncio
import importlib.resources
import time

__docformat__ = "google"
def process_video_files(
    root_dir: Union[str, Path],
    namer_config: str,
    suffix: Tuple[str, ...] = (".m4v", ".mp4"),
    endswith: str = "",
) -> None:
    """
    Recursively finds and processes .m4v and .mp4 files in subfolders of root_dir.

    Args:
        root_dir (str or Path): The starting directory.
        namer_config (str): Path to the namer configuration file.
        suffix (tuple): Tuple of file extensions to process.
        endswith (str): process files whose file stems end with defined string .
    """
    root_dir = Path(root_dir)  # Ensure root_dir is a Path object
    if not root_dir.exists():
        print(f"Error: Directory '{root_dir}' not found.")
        return

    items = list(root_dir.rglob("*"))  # Use rglob to recursively find all files
    random.shuffle(items)

    async def async_run_namer_command(item, namer_config, semaphore):
        async with semaphore:
            print(f"Processing file: {item}") # Moved this line here
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, run_namer_command, item, namer_config)

    async def process_all(items, suffix, endswith, namer_config):
        semaphore = asyncio.Semaphore(2)  # Limit concurrency to 2
        tasks = []
        for item in items:
            if (
                item.is_file()
                and (item.suffix.lower() in suffix)
                and str(item.stem).lower().endswith(endswith)
            ):
                tasks.append(async_run_namer_command(item, namer_config, semaphore))
        await asyncio.gather(*tasks)

    asyncio.run(process_all(items, suffix, endswith, namer_config))
    exit(0)


def run_namer_command(
    directory: Path, namer_config: str = ".namer.cfg"
) -> tuple[str | None, str, int]:
    """
    Executes a shell command to process files in a directory.
    Tries to fetch from jellyfin generated nfo first. If fails, tries to rename using theporndb.net.

    Args:
        directory (Path): The directory to process.
        namer_config (str): Path to the namer configuration file.

    Returns:
        tuple: A tuple containing (stdout, stderr, returncode).
    """
    try:
        is_windows = platform.system().lower() == "windows"
        # print(f"Detected OS: {'Windows' if is_windows else 'Non-Windows'}")
        if is_windows:
            shell = True
            cmd = f'python -m namer rename -c "{namer_config}" -f "{str(directory)}" -i -v'
        else:
            shell = False
            cmd = [
            "python",
            "-m",
            "namer",
            "rename",
            "-c",
            namer_config,
            "-f",
            str(directory),
            "-i",
            "-v",
            ]

        print(f"Try loading from nfo. Processing file: {directory}")
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=shell,
        )
        stdout = process.stdout
        stderr = process.stderr
        returncode = process.returncode
        print(stdout)
        #print(returncode)
        # if returncode==0:
        #     print(f"NFO: Fail to match {directory} with nfo: {stderr}. Try the PornDB again.")
        if returncode == 1:
            print(f"NFO: Successfully match {directory} with nfo. Try the PornDB again.")
        time.sleep(random.random()*5+0.5)
        if is_windows:
            shell = True
            cmd = f'python -m namer rename -c "{namer_config}" -f "{str(directory)}" -v'
        else:
            shell = False
            cmd = [
            "python",
            "-m",
            "namer",
            "rename",
            "-c",
            namer_config,
            "-f",
            str(directory),
            "-v",
            ]
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=shell,
        )
        print(process.stdout)
        print(process.stderr)
        #print(process.returncode)
        if process.returncode == 1:
            print(f"PornDB: ✅ Successfully match {directory} with PornDB metadata.")
        else:
            print(f"PornDB: Failed to match {directory} with PornDB metadata")
        return stdout, stderr, returncode
    except Exception as e:
        print(f"Exception occurred while processing {directory}: {e}")
        return None, str(e), -1


def get_leaf_directories(root_path: Path) -> list[Path]:
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


def process_leaf_files(root_dir: Path, namer_config: str = ".namer.cfg") -> None:
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
    NAMER_CONFIG_DEFAULT = str(importlib.resources.files('ExplicitUtil').joinpath('config/.namer.cfg'))
    # print(NAMER_CONFIG_DEFAULT)
    ROOT_DIR = Path(
        input("Enter the folder path to video files: ")
    )  # replace with your directory.
    if not ROOT_DIR.is_dir():
        print(f"Error: Directory '{ROOT_DIR}' not found.")
        exit(1)
    NAMER_CONFIG = input(
        "Enter the path to the namer configuration file (.namer.cfg) or hit enter to load default: "
    )
    if NAMER_CONFIG == "":
        NAMER_CONFIG = NAMER_CONFIG_DEFAULT
    if not Path(NAMER_CONFIG).is_file():
        print(f"Error: Configuration file '{NAMER_CONFIG}' not found.")
    process_video_files(ROOT_DIR, NAMER_CONFIG, suffix=(".m4v", ".mp4"), endswith="")
