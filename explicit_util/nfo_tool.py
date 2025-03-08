import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import re

def process_single_file(file_path, media_type, output_path):
    base_name = file_path.stem
    nfo_filename = output_path / f"{base_name}.nfo"
    date = detect_date_in_name(base_name)
    if media_type == "movie":
        if nfo_filename.exists():
            update_movie_nfo(str(nfo_filename), base_name, date)
        else:
            create_movie_nfo(str(nfo_filename), base_name, date)
    elif media_type == "episode":
        if nfo_filename.exists():
            update_episode_nfo(str(nfo_filename), base_name, date)
        else:
            create_episode_nfo(str(nfo_filename), base_name, date)
    elif media_type == "musicvideo":
        if nfo_filename.exists():
            update_movie_nfo(str(nfo_filename), base_name, date)
        else:
            create_movie_nfo(str(nfo_filename), base_name, date)

def generate_nfo(media_path, media_type, output_dir="nfo_files"):
    """
    Generates .nfo files for media in a given directory and subdirectories.

    Args:
        media_path (str): Path to the media directory.
        media_type (str): Type of media (movie, tvshow, season, episode, artist, album, musicvideo).
        output_dir (str): Directory to save the generated .nfo files.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    media_path_obj = Path(media_path)

    if media_type in ["movie", "episode", "musicvideo"]:
        for file_path in media_path_obj.rglob("*"):  # rglob for recursive globbing
            if file_path.is_file() and file_path.suffix.lower() in (".m4v", ".mp4", ".mkv", ".avi", ".mov", ".iso", ".vob", ".m2ts"):
                relative_path = file_path.relative_to(media_path_obj)
                file_output_path = output_path / relative_path.parent
                process_single_file(file_path, media_type, file_output_path)
    elif media_type == "tvshow":
        nfo_filename = output_path / "tvshow.nfo"
        if not nfo_filename.exists():
            create_tvshow_nfo(str(nfo_filename))
    elif media_type == "season":
        nfo_filename = output_path / "season.nfo"
        if not nfo_filename.exists():
            create_season_nfo(str(nfo_filename))
    elif media_type == "artist":
        nfo_filename = output_path / "artist.nfo"
        if not nfo_filename.exists():
            create_artist_nfo(str(nfo_filename))
    elif media_type == "album":
        nfo_filename = output_path / "album.nfo"
        if not nfo_filename.exists():
            create_album_nfo(str(nfo_filename))
    else:
        print("Invalid media type.")

def detect_date_in_name(name):
    """Detects a date in the file name and returns it in YYYY-MM-DD format."""
    date_patterns = [
        r"(\d{4})[-_.](\d{2})[-_.](\d{2})",  # YYYY-MM-DD or YYYY_MM_DD or YYYY.MM.DD
        r"(\d{2})[-_.](\d{2})[-_.](\d{4})",   # DD-MM-YYYY or DD_MM_YYYY or DD.MM.YYYY
        r"(\d{2})[-._](\d{2})[-._](\d{2})"   # YY-MM-DD or YY_MM_DD or YY.MM.DD
    ]
    for pattern in date_patterns:
        match = re.search(pattern, name)
        if match:
            if len(match.groups()) == 3:
                year, month, day = match.groups()
                if len(year) == 4:
                    return f"{year}-{month}-{day}"
                elif len(day) == 4:
                    return f"{day}-{month}-{year}"
                elif len(year) == 2:
                    year = "20" + year if int(year) < 25 else "19" + year
                    return f"{year}-{month}-{day}"
    return None

def create_movie_nfo(nfo_filename, title, date=None):
    """Creates a basic movie .nfo file."""
    root = ET.Element("movie")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = title
    if date:
        premiered_elem = ET.SubElement(root, "premiered")
        premiered_elem.text = date
        releasedate_elem = ET.SubElement(root, "releasedate")
        releasedate_elem.text = date
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def update_movie_nfo(nfo_filename, title, date=None):
    """Updates an existing movie .nfo file."""
    tree = ET.parse(nfo_filename)
    root = tree.getroot()
    title_elem = root.find("title")
    if title_elem is None:
        title_elem = ET.SubElement(root, "title")
        title_elem.text = title
    if date:
        premiered_elem = root.find("premiered")
        if premiered_elem is None:
            premiered_elem = ET.SubElement(root, "premiered")
        premiered_elem.text = date
        releasedate_elem = root.find("releasedate")
        if releasedate_elem is None:
            releasedate_elem = ET.SubElement(root, "releasedate")
        releasedate_elem.text = date
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def create_tvshow_nfo(nfo_filename):
    root = ET.Element("tvshow")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = "TV Show Title"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def create_season_nfo(nfo_filename):
    root = ET.Element("season")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = "Season Title"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def create_episode_nfo(nfo_filename, title, date=None):
    root = ET.Element("episodedetails")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = title
    if date:
        premiered_elem = ET.SubElement(root, "premiered")
        premiered_elem.text = date
        releasedate_elem = ET.SubElement(root, "releasedate")
        releasedate_elem.text = date
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def update_episode_nfo(nfo_filename, title, date=None):
    """Updates an existing episode .nfo file."""
    tree = ET.parse(nfo_filename)
    root = tree.getroot()
    title_elem = root.find("title")
    if title_elem is None:
        title_elem = ET.SubElement(root, "title")
    title_elem.text = title
    if date:
        premiered_elem = root.find("premiered")
        if premiered_elem is None:
            premiered_elem = ET.SubElement(root, "premiered")
        premiered_elem.text = date
        releasedate_elem = root.find("releasedate")
        if releasedate_elem is None:
            releasedate_elem = ET.SubElement(root, "releasedate")
        releasedate_elem.text = date
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def create_artist_nfo(nfo_filename):
    root = ET.Element("artist")
    name_elem = ET.SubElement(root, "name")
    name_elem.text = "Artist Name"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def create_album_nfo(nfo_filename):
    root = ET.Element("album")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = "Album Title"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)

def batch_add_attribute(nfo_dir, attribute, value, role=None, type_actor="Actor", thumb=None):
    """
    Batch adds an attribute to existing .nfo files.

    Args:
        nfo_dir (str): Directory containing .nfo files.
        attribute (str): Attribute to add (e.g., studio, actor, year).
        value (str): Value of the attribute.
        role (str): Role of the actor.
        type_actor (str): Type of actor.
        thumb (str): Path to the actor's thumbnail.
    """
    nfo_path_obj = Path(nfo_dir)
    for file_path in nfo_path_obj.rglob("*.nfo"):  # Use rglob to search in subfolders
        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()

            if attribute == "actor":
                existing_actors = [actor.find("name").text for actor in root.findall("actor") if actor.find("name") is not None]
                if value not in existing_actors:
                    actor_elem = ET.SubElement(root, "actor")
                    name_elem = ET.SubElement(actor_elem, "name")
                    name_elem.text = value
                    if role:
                        role_elem = ET.SubElement(actor_elem, "role")
                        role_elem.text = role
                    if type_actor:
                        type_elem = ET.SubElement(actor_elem, "type")
                        type_elem.text = type_actor
                    if thumb:
                        thumb_elem = ET.SubElement(actor_elem, "thumb")
                        thumb_elem.text = thumb

            elif attribute == "year":
                if root.find("year") is None:
                    year_elem = ET.SubElement(root, "year")
                    year_elem.text = value
            elif value in root.findall(attribute):
                # If the attribute already exists, skip adding it
                continue
            else:
                # For other attributes, just add the element                 
                new_elem = ET.SubElement(root, attribute)
                new_elem.text = value

            tree.write(str(file_path), encoding="utf-8", xml_declaration=True)
        except ET.ParseError:
            print(f"Error parsing {file_path.name}. Skipping.")

# Example usage
media_folder = "media"  # Replace with your media folder
nfo_output_folder = "nfo_files"

# Generate nfo files for movies in subfolders
generate_nfo(media_folder, "movie", nfo_output_folder)

# Add actor, studio and year to all generated movie .nfo files
batch_add_attribute(nfo_output_folder, "studio", "Example Studio")
batch_add_attribute(nfo_output_folder, "year", "2023")
batch_add_attribute(nfo_output_folder, "actor", "Cadence Kline", role="Transgender Female", type_actor="Actor", thumb="E:\\Jellyfin\\Server\\metadata\\People\\C\\Cadence Kline\\folder.png")

#Generate nfo for tv shows, episodes, artists or albums.
#generate_nfo(media_folder, "tvshow", nfo_output_folder)
#generate_nfo(media_folder, "episode", nfo_output_folder)
#generate_nfo(media_folder, "artist", nfo_output_folder)
#generate_nfo(media_folder, "album", nfo_output_folder)
#generate_nfo(media_folder