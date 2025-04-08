from .convert_pic_to_webp import convert_pic_to_webp_multithreaded
from .nfo_tool import generate_nfo
from .recursive_namer import process_video_files
from .recursive_unzip import recursive_unzip
from .remove_empty import remove_empty_folders
from .whisper_cpp_transcribe import process_videos, get_input_folder
from .zip_and_move import async_zip_and_move
import importlib.resources
import os
from pathlib import Path
import asyncio
import toml


def choice1():
    """Convert images to WebP format."""
    config_path = Path(str(importlib.resources.files('ExplicitUtil').joinpath('config/convert_pic_to_webp.toml')))
    config_path.parent.mkdir(parents=True, exist_ok=True)
    default_config = {"num_threads": 6, "timeout": 10, "quality": 80}

    # Load configuration from file if available
    if config_path.is_file():
        try:
            config = toml.load(config_path)
            use_config = input("Use stored config for settings? (y/n): ").strip().lower() == "y"
            if use_config:
                default_config.update({k: config.get(k, v) for k, v in default_config.items()})
        except Exception as e:
            print(f"Error loading config file: {e}")
            return
    else:
        print("Config file not found. Using manual input.")
        # Prompt for settings if not using config
        for key, default in default_config.items():
            value = input(f"Enter {key.replace('_', ' ')} (default: {default}): ").strip()
            if value:
                try:
                    default_config[key] = int(value)
                except ValueError:
                    print(f"Invalid input for {key}. Using default: {default}.")
    with open(config_path, "w") as config_file:
        toml.dump(default_config, config_file)
        print(f"Config saved to {config_path}")
    folder_path = input("Enter the folder path to convert picture files: ").strip('"')
    if not Path(folder_path).exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    try:
        convert_pic_to_webp_multithreaded(
            folder_path=folder_path,
            num_threads=default_config["num_threads"],
            timeout=default_config["timeout"],
            quality=default_config["quality"],
        )
    except Exception as e:
        print(f"Error converting files: {e}")

def choice2():
    """generate nfo files"""
    media_path = input("Enter the media directory path: ")
    if not Path(media_path).exists():
        print(f"Error: Media directory '{media_path}' does not exist.")
        exit(1)
    media_type = input("Enter the media type (movie, episode, musicvideo): ")
    output_dir = input("Enter the output directory path: ")
    if not Path(output_dir).exists():
        print(f"Output directory '{output_dir}' does not exist. Makeing it now.")
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error creating output directory: {e}")
            exit(1)
    try:
        generate_nfo(media_path, media_type, output_dir)
        return
    except Exception as e:
        print(f"Error generating NFO files: {e}")
        return
    

def choice3():
    """process video files"""
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
    try:
        process_video_files(ROOT_DIR, NAMER_CONFIG, suffix=(".m4v", ".mp4"), endswith=())
        return
    except Exception as e:
        print(f"Error processing video files: {e}")
        return

def choice4():
    """unzip files recursively"""
    folder_path = Path(input("Enter the folder path to unzip files: ").strip('"'))
    delete_zips = input("Delete ZIP archives after unzipping? (y/n): ").strip().lower()=='y'

    if not folder_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    try:
        recursive_unzip(folder_path, delete_zips)
        return
    except Exception as e:
        print(f"Error unzipping files: {e}")
        return


def choice5():
    """remove empty folders"""
    target_dir = input("Please enter the target directory: ").strip("\"")
    dry_run = input("Do you want to perform a dry run? (y/n): ").strip().lower() == 'y'
    
    if not Path(target_dir).exists():
        print(f"Error: Folder '{target_dir}' does not exist.")
        return
    
    try:
        remove_empty_folders(target_dir, dry_run)
        return
    except Exception as e:
        print(f"Error removing empty folders: {e}")
        return


def choice6():
    """transcribe videos with Whisper.cpp"""
    input_folder, whisper_root = get_input_folder()
    suffix = input(
        "Enter the file extensions to process (comma-separated, e.g., .m4v,.mp4): "
    )
    suffix = tuple(ext.strip() for ext in suffix.split(","))
    if suffix == ("",):
        print("No file extensions provided. Use default: .m4v,.mp4")
        suffix = (".m4v", ".mp4")
    prompt = input(
        "Enter the prompt for Whisper transcription (leave blank for none): "
    )
    process_videos(input_folder, whisper_root, prompt=prompt, suffix=suffix)
    return



def choice7():
    """zip and move folders"""
    source_folder = Path(input("Enter the source folder path: ").strip("\""))
    if not source_folder.is_dir():
        print(f"The folder '{source_folder}' does not exist.")
        return
    destination_folder = Path(input("Enter the destination folder path: "))
    if not destination_folder.is_dir():
        print(f"The folder '{destination_folder}' does not exist.")
        destination_folder.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(async_zip_and_move(source_folder, destination_folder))
        return
    except Exception as e:
        print(f"Error zipping and moving folders: {e}")
        return

def main():
    while True:
        print("ExplicitUtil CLI")
        print("1. Convert images to WebP")
        print("2. Generate NFO files")
        print("3. Process video files")
        print("4. Unzip files recursively")
        print("5. Remove empty folders")
        print("6. Transcribe videos with Whisper.cpp")
        print("7. Zip and move folders")

        choice = input("Choose an option (1-7): ")
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 7.")
            continue

        if choice == 1:
            choice1()
        elif choice == 2:
            choice2()
        elif choice == 3:
            choice3()
        elif choice == 4:
            choice4()
        elif choice == 5:
            choice5()
        elif choice == 6:
            choice6()
        elif choice == 7:
            choice7()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
