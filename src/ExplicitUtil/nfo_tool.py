import xml.etree.ElementTree as ET
from pathlib import Path
import re
from typing import Optional

__docformat__ = "google"

def process_single_file(file_path: Path, output_path: Path) -> None:
    """Processes a single media file to generate or update its .nfo file as a movie."""
    base_name = file_path.stem
    nfo_filename = output_path / f"{base_name}.nfo"
    date = detect_date_in_name(base_name)
    
    if nfo_filename.exists():
        update_movie_nfo(str(nfo_filename), base_name, date)
    else:
        create_movie_nfo(str(nfo_filename), base_name, date)


def generate_nfo(media_path: str, output_dir: str) -> None:
    """Generates movie .nfo files for media in a given directory and subdirectories."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    media_path_obj = Path(media_path)

    for file_path in media_path_obj.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in (
            ".m4v", ".mp4", ".mkv", ".avi", ".mov", ".iso", ".vob", ".m2ts",
        ):
            relative_path = file_path.relative_to(media_path_obj)
            file_output_path = output_path / relative_path.parent
            file_output_path.mkdir(parents=True, exist_ok=True)
            process_single_file(file_path, file_output_path)


def detect_date_in_name(name: str) -> Optional[str]:
    """Detects a date in the file name and returns it in YYYY-MM-DD format."""
    date_patterns = [
        r"(\d{4})[-_.](\d{2})[-_.](\d{2})",
        r"(\d{2})[-_.](\d{2})[-_.](\d{4})",
        r"(\d{2})[-._](\d{2})[-._](\d{2})",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, name)
        if match:
            if len(match.groups()) == 3:
                year, month, day = match.groups()
                if len(year) == 4: return f"{year}-{month}-{day}"
                elif len(day) == 4: return f"{day}-{month}-{year}"
                elif len(year) == 2:
                    year = "20" + year if int(year) < 25 else "19" + year
                    return f"{year}-{month}-{day}"
    return None


def create_movie_nfo(nfo_filename: str, title: str, date: str | None = None) -> None:
    root = ET.Element("movie")
    title_elem = ET.SubElement(root, "title")
    title_elem.text = title
    if date:
        ET.SubElement(root, "premiered").text = date
        ET.SubElement(root, "releasedate").text = date
    tree = ET.ElementTree(root)
    tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)


def update_movie_nfo(nfo_filename: str, title: str, date: str | None = None) -> None:
    try:
        tree = ET.parse(nfo_filename)
        root = tree.getroot()
        if root.tag != "movie":
            # If it's not a movie NFO, we might want to convert or skip.
            # For simplicity, we'll ensure it has movie tag if we are treating all as movie.
            root.tag = "movie"
        
        if root.find("title") is None:
            ET.SubElement(root, "title").text = title
        if date:
            if root.find("premiered") is None: ET.SubElement(root, "premiered").text = date
            if root.find("releasedate") is None: ET.SubElement(root, "releasedate").text = date
        tree.write(nfo_filename, encoding="utf-8", xml_declaration=True)
    except ET.ParseError:
        print(f"Error parsing {nfo_filename}. Creating new.")
        create_movie_nfo(nfo_filename, title, date)


def batch_add_tag(nfo_dir: Path | str, tag_name: str) -> None:
    """Adds a tag to all .nfo files in a directory if it doesn't already exist."""
    nfo_path_obj = Path(nfo_dir)
    for file_path in nfo_path_obj.rglob("*.nfo"):
        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            modified = False
            
            existing_tags = [t.text for t in root.findall("tag") if t.text]
            if tag_name not in existing_tags:
                ET.SubElement(root, "tag").text = tag_name
                modified = True
            
            if modified:
                tree.write(str(file_path), encoding="utf-8", xml_declaration=True)
                print(f"Added tag '{tag_name}' to {file_path.name}")
        except ET.ParseError:
            print(f"Error parsing {file_path.name}. Skipping.")

def batch_add_actor(
    nfo_dir: Path | str, 
    name: str, 
    role: Optional[str] = None, 
    type_actor: str = "Actor", 
    thumb: Optional[str] = None
) -> None:
    """Adds an actor/artist to all .nfo files in a directory if they don't already exist."""
    nfo_path_obj = Path(nfo_dir)
    for file_path in nfo_path_obj.rglob("*.nfo"):
        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            modified = False
            
            existing_actors = []
            for actor in root.findall("actor"):
                name_elem = actor.find("name")
                if name_elem is not None and name_elem.text:
                    existing_actors.append(name_elem.text)
            
            if name not in existing_actors:
                actor_elem = ET.SubElement(root, "actor")
                ET.SubElement(actor_elem, "name").text = name
                if role: ET.SubElement(actor_elem, "role").text = role
                if type_actor: ET.SubElement(actor_elem, "type").text = type_actor
                if thumb: ET.SubElement(actor_elem, "thumb").text = thumb
                modified = True
            
            if modified:
                tree.write(str(file_path), encoding="utf-8", xml_declaration=True)
                print(f"Added actor '{name}' to {file_path.name}")
        except ET.ParseError:
            print(f"Error parsing {file_path.name}. Skipping.")

def batch_add_attribute(
    nfo_dir: str,
    attribute: str,
    value: str,
    role: Optional[str] = None,
    type_actor: str = "Actor",
    thumb: Optional[str] = None,
) -> None:
    """Legacy generic function for batch adding attributes."""
    if attribute == "tag":
        batch_add_tag(nfo_dir, value)
    elif attribute in ["actor", "artist"]:
        batch_add_actor(nfo_dir, value, role, type_actor, thumb)
    else:
        nfo_path_obj = Path(nfo_dir)
        for file_path in nfo_path_obj.rglob("*.nfo"):
            try:
                tree = ET.parse(str(file_path))
                root = tree.getroot()
                if root.find(attribute) is None or root.find(attribute).text != value:
                    ET.SubElement(root, attribute).text = value
                    tree.write(str(file_path), encoding="utf-8", xml_declaration=True)
            except ET.ParseError:
                pass

if __name__ == "__main__":
    print("Use 'python -m ExplicitUtil nfo' for the modern CLI.")
