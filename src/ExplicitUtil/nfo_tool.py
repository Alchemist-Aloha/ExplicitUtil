import xml.etree.ElementTree as ET
from pathlib import Path
import re


def process_single_file(file_path: Path, media_type: str, output_path: Path) -> None:
    """Processes a single media file to generate or update its .nfo file.
    Args:
        file_path (Path): Path to the media file.
        media_type (str): Type of media (movie, episode, musicvideo).
        output_path (Path): Directory to save the generated .nfo file.
    """
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


def generate_nfo(media_path: str, media_type: str, output_dir: str) -> None:
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
            if file_path.is_file() and file_path.suffix.lower() in (
                ".m4v",
                ".mp4",
                ".mkv",
                ".avi",
                ".mov",
                ".iso",
                ".vob",
                ".m2ts",
            ):
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


def detect_date_in_name(name: str) -> str | None:
    """Detects a date in the file name and returns it in YYYY-MM-DD format.
    Args:
        name (str): The file name to search for a date.
        Returns:
            str: The detected date in YYYY-MM-DD format, or None if no date is found.
    """
    date_patterns = [
        r"(\d{4})[-_.](\d{2})[-_.](\d{2})",  # YYYY-MM-DD or YYYY_MM_DD or YYYY.MM.DD
        r"(\d{2})[-_.](\d{2})[-_.](\d{4})",  # DD-MM-YYYY or DD_MM_YYYY or DD.MM.YYYY
        r"(\d{2})[-._](\d{2})[-._](\d{2})",  # YY-MM-DD or YY_MM_DD or YY.MM.DD
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


def create_movie_nfo(nfo_filename: str, title: str, date: str | None = None) -> None:
    """Creates a basic movie .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to create.
        title (str): Title of the movie.
        date (str): Release date of the movie in YYYY-MM-DD format.
    """
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


def update_movie_nfo(nfo_filename: str, title: str, date: str | None = None) -> None:
    """Updates an existing movie .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to update.
        title (str): Title of the movie.
        date (str): Release date of the movie in YYYY-MM-DD format.
    """
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


def create_tvshow_nfo(nfo_filename: str) -> None:
    """Creates a basic TV show .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to create.
    """
    root = ET.Element("tvshow")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = "TV Show Title"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)


def create_season_nfo(nfo_filename: str) -> None:
    """Creates a basic season .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to create.
    """
    root = ET.Element("season")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = "Season Title"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)


def create_episode_nfo(nfo_filename: str, title: str, date: str | None = None) -> None:
    """Creates a basic episode .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to create.
        title (str): Title of the episode.
        date (str): Release date of the episode in YYYY-MM-DD format.
    """
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


def update_episode_nfo(nfo_filename: str, title: str, date: str | None = None) -> None:
    """Updates an existing episode .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to update.
        title (str): Title of the episode.
        date (str): Release date of the episode in YYYY-MM-DD format.
    """
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


def create_artist_nfo(nfo_filename: str) -> None:
    """Creates a basic artist .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to create.
    """
    root = ET.Element("artist")
    name_elem = ET.SubElement(root, "name")
    name_elem.text = "Artist Name"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)


def create_album_nfo(nfo_filename: str) -> None:
    """Creates a basic album .nfo file.
    Args:
        nfo_filename (str): Path to the .nfo file to create.
    """
    root = ET.Element("album")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = "Album Title"
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)


def batch_add_attribute(
    nfo_dir: str,
    attribute: str,
    value: str,
    role: None | str = None,
    type_actor: str = "Actor",
    thumb: str | None = None,
) -> None:
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
                # Find all existing actors in the XML
                existing_actors = []
                for actor in root.findall("actor"):
                    name_elem = actor.find("name")
                    if name_elem is not None and name_elem.text is not None:
                        existing_actors.append(name_elem.text)
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


if __name__ == "__main__":
    media_path = input("Enter the media directory path: ")
    media_type = input("Enter the media type (movie, episode, musicvideo): ")
    output_dir = input("Enter the output directory path: ")
    generate_nfo(media_path, media_type, output_dir)
