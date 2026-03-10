import typer
from typing import Optional, List, Any
from pathlib import Path
import asyncio
import os
import toml
import importlib.resources
from .convert_pic_to_webp import convert_pic_to_webp_multithreaded
from .nfo_tool import generate_nfo, batch_add_tag, batch_add_actor, batch_add_studio
from .recursive_namer import process_video_files
from .recursive_unzip import recursive_unzip
from .remove_empty import remove_empty_folders
from .whisper_cpp_transcribe import transcribe_videos
from .zip_and_move import async_zip_and_move
from .group_files import group_files_by_string, move_grouped_files

app = typer.Typer(help="ExplicitUtil: A utility library for managing media files.")

def get_config_path(config_name: str) -> Path:
    config_path = Path(str(importlib.resources.files('ExplicitUtil').joinpath(f'config/{config_name}.toml')))
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path

def load_config(config_name: str, default_values: dict) -> dict:
    config_path = get_config_path(config_name)
    if config_path.is_file():
        try:
            config = toml.load(config_path)
            return {**default_values, **config}
        except Exception as e:
            typer.echo(f"Error loading config file: {e}", err=True)
    return default_values

def save_config(config_name: str, config_values: dict):
    config_path = get_config_path(config_name)
    try:
        with open(config_path, "w") as config_file:
            toml.dump(config_values, config_file)
        typer.echo(f"Config saved to {config_path}")
    except Exception as e:
        typer.echo(f"Error saving config file: {e}", err=True)

def merge_settings(config_name: str, cli_settings: dict, defaults: dict) -> dict:
    stored_settings = load_config(config_name, defaults)
    final_settings = {**stored_settings, **{k: v for k, v in cli_settings.items() if v is not None}}
    return final_settings

@app.command()
def convert_pic(
    folder_path: Path = typer.Argument(..., help="Folder path to convert images"),
    num_threads: Optional[int] = typer.Option(None, help="Number of threads (default: 6)"),
    timeout: Optional[int] = typer.Option(None, help="Timeout in seconds (default: 10)"),
    quality: Optional[int] = typer.Option(None, help="WebP quality (default: 80)"),
    save: bool = typer.Option(False, "--save", help="Save these settings to config"),
):
    """Convert images to WebP format. Uses stored config by default."""
    config_name = "convert_pic_to_webp"
    defaults = {"num_threads": 6, "timeout": 10, "quality": 80}
    cli_settings = {"num_threads": num_threads, "timeout": timeout, "quality": quality}
    settings = merge_settings(config_name, cli_settings, defaults)
    if save: save_config(config_name, settings)

    if not folder_path.exists():
        typer.echo(f"Error: Folder '{folder_path}' does not exist.", err=True)
        raise typer.Exit(1)

    try:
        convert_pic_to_webp_multithreaded(
            folder_path=str(folder_path),
            num_threads=settings["num_threads"],
            timeout=settings["timeout"],
            quality=settings["quality"],
        )
    except Exception as e:
        typer.echo(f"Error converting files: {e}", err=True)

@app.command()
def nfo(
    media_path: Path = typer.Argument(..., help="Media directory path"),
    output_dir: Optional[Path] = typer.Option(None, help="Output directory path"),
):
    """Generate movie NFO files for media."""
    if not media_path.exists():
        typer.echo(f"Error: Media directory '{media_path}' does not exist.", err=True)
        raise typer.Exit(1)
    
    out_dir = output_dir or media_path
    if not out_dir.exists():
        typer.echo(f"Output directory '{out_dir}' does not exist. Creating it.")
        out_dir.mkdir(parents=True, exist_ok=True)

    try:
        generate_nfo(str(media_path), str(out_dir))
    except Exception as e:
        typer.echo(f"Error generating NFO files: {e}", err=True)

@app.command()
def nfo_tag(
    nfo_dir: Path = typer.Argument(..., help="Directory containing .nfo files"),
    tag: str = typer.Argument(..., help="Tag name to add"),
):
    """Batch add a tag to NFO files."""
    if not nfo_dir.is_dir():
        typer.echo(f"Error: Directory '{nfo_dir}' not found.", err=True)
        raise typer.Exit(1)
    batch_add_tag(nfo_dir, tag)

@app.command()
def nfo_studio(
    nfo_dir: Path = typer.Argument(..., help="Directory containing .nfo files"),
    studio: str = typer.Argument(..., help="Studio name to set"),
):
    """Batch set a studio in NFO files."""
    if not nfo_dir.is_dir():
        typer.echo(f"Error: Directory '{nfo_dir}' not found.", err=True)
        raise typer.Exit(1)
    batch_add_studio(nfo_dir, studio)

@app.command()
def nfo_actor(
    nfo_dir: Path = typer.Argument(..., help="Directory containing .nfo files"),
    name: str = typer.Argument(..., help="Actor/Artist name"),
    role: Optional[str] = typer.Option(None, help="Role of the actor"),
):
    """Batch add an actor/artist to NFO files."""
    if not nfo_dir.is_dir():
        typer.echo(f"Error: Directory '{nfo_dir}' not found.", err=True)
        raise typer.Exit(1)
    batch_add_actor(nfo_dir, name, role=role)

@app.command()
def rename(
    folder_path: Path = typer.Argument(..., help="Folder path to video files"),
    namer_config: Optional[Path] = typer.Option(None, help="Path to namer config file"),
    suffix: Optional[str] = typer.Option(None, help="Suffixes to process (comma-separated, default: .m4v,.mp4)"),
    endswith: Optional[str] = typer.Option(None, help="Endswith string (case-insensitive)"),
    save: bool = typer.Option(False, "--save", help="Save these settings to config"),
):
    """Batch rename video files with namer. Uses stored config by default."""
    config_name = "recursive_namer"
    default_namer_path = str(importlib.resources.files('ExplicitUtil').joinpath('config/.namer.cfg'))
    defaults = {"namer_config_path": default_namer_path, "suffix": [".m4v", ".mp4"], "endswith": ""}
    cli_settings = {}
    if namer_config: cli_settings["namer_config_path"] = str(namer_config)
    if suffix: cli_settings["suffix"] = [ext.strip() for ext in suffix.split(",")]
    if endswith is not None: cli_settings["endswith"] = endswith
    settings = merge_settings(config_name, cli_settings, defaults)
    if save: save_config(config_name, settings)

    if not folder_path.is_dir():
        typer.echo(f"Error: Directory '{folder_path}' not found.", err=True)
        raise typer.Exit(1)

    try:
        process_video_files(
            root_dir=folder_path,
            namer_config=settings['namer_config_path'],
            suffix=tuple(settings["suffix"]),
            endswith=settings["endswith"]
        )
    except Exception as e:
        typer.echo(f"Error processing video files: {e}", err=True)

@app.command()
def unzip(
    folder_path: Path = typer.Argument(..., help="Folder path to unzip files"),
    delete_zips: bool = typer.Option(False, "--delete", "-d", help="Delete ZIP archives after unzipping"),
):
    """Unzip files recursively."""
    if not folder_path.exists():
        typer.echo(f"Error: Folder '{folder_path}' does not exist.", err=True)
        raise typer.Exit(1)

    try:
        recursive_unzip(folder_path, delete_zips)
    except Exception as e:
        typer.echo(f"Error unzipping files: {e}", err=True)

@app.command()
def remove_empty(
    target_dir: Path = typer.Argument(..., help="Target directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Perform a dry run"),
):
    """Remove empty folders."""
    if not target_dir.exists():
        typer.echo(f"Error: Folder '{target_dir}' does not exist.", err=True)
        raise typer.Exit(1)
    
    try:
        remove_empty_folders(str(target_dir), dry_run)
    except Exception as e:
        typer.echo(f"Error removing empty folders: {e}", err=True)

@app.command()
def transcribe(
    input_folder: Path = typer.Argument(..., help="Folder path to video files"),
    whisper_root: Optional[Path] = typer.Option(None, help="Path to whisper.cpp root directory"),
    prompt: Optional[str] = typer.Option(None, help="Prompt for Whisper transcription"),
    suffix: Optional[str] = typer.Option(None, help="Suffixes to process (comma-separated, default: .m4v,.mp4,.mkv)"),
    save: bool = typer.Option(False, "--save", help="Save these settings to config"),
):
    """Transcribe videos with Whisper.cpp. Uses stored config by default."""
    config_name = "whisper_cpp_transcribe"
    defaults = {"whisper_root": "", "suffix": [".m4v", ".mp4", ".mkv"], "prompt": ""}
    cli_settings = {}
    if whisper_root: cli_settings["whisper_root"] = str(whisper_root)
    if prompt is not None: cli_settings["prompt"] = prompt
    if suffix: cli_settings["suffix"] = [ext.strip() for ext in suffix.split(",")]
    settings = merge_settings(config_name, cli_settings, defaults)
    if save: save_config(config_name, settings)

    if not settings["whisper_root"]:
        typer.echo("Error: whisper_root is required. Use --whisper-root or set it in config.", err=True)
        raise typer.Exit(1)

    try:
        transcribe_videos(str(input_folder), settings["whisper_root"], prompt=settings["prompt"], suffix=tuple(settings["suffix"]))
    except Exception as e:
        typer.echo(f"Error transcribing videos: {e}", err=True)

@app.command()
def archive(
    source_folder: Path = typer.Argument(..., help="Source folder path"),
    destination_folder: Path = typer.Argument(..., help="Destination folder path"),
):
    """Zip and move folders asynchronously."""
    if not source_folder.is_dir():
        typer.echo(f"Error: Source folder '{source_folder}' does not exist.", err=True)
        raise typer.Exit(1)
    
    if not destination_folder.is_dir():
        typer.echo(f"Destination folder '{destination_folder}' does not exist. Creating it.")
        destination_folder.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(async_zip_and_move(source_folder, destination_folder))
    except Exception as e:
        typer.echo(f"Error archiving folders: {e}", err=True)

@app.command()
def group(
    directory: Path = typer.Argument(..., help="Directory path to group files"),
    regex: str = typer.Option(r"(\d{4}-\d{2}-\d{2})", help="Regex pattern to match"),
    move: bool = typer.Option(False, "--move", "-m", help="Move files after grouping"),
):
    """Group files by regex matching."""
    if not directory.is_dir():
        typer.echo(f"Error: Directory '{directory}' not found.", err=True)
        raise typer.Exit(1)

    grouped_files = group_files_by_string(directory, regex)
    for key, files in grouped_files.items():
        typer.echo(f"{key}: {len(files)} files")
    
    if move:
        move_grouped_files(directory, grouped_files)
        typer.echo("Files moved successfully.")
    else:
        typer.echo("Dry run complete. Use --move to actually move files.")

@app.command()
def merge(
    video_files: List[str] = typer.Argument(..., help="List of video file paths to merge"),
    output_file: Path = typer.Argument(..., help="Output merged video file path"),
):
    """Merge videos using ffmpeg."""
    from .merge_videos import merge_videos
    try:
        merge_videos(video_files, str(output_file))
    except Exception as e:
        typer.echo(f"Error merging videos: {e}", err=True)

def main():
    app()

if __name__ == "__main__":
    main()
