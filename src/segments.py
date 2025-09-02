import json
import os
import re
import unicodedata

# Base directories
DATA_DIR = 'data'
EVENTS_DATA_DIR = os.path.join(DATA_DIR, 'events')
INCLUDES_DIR = 'includes'
TMP_DIR = os.path.join(INCLUDES_DIR, 'tmp')

def _get_project_root():
    """Returns the absolute path to the project root directory."""
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, os.pardir))

def _get_segments_file_path(event_slug):
    """Constructs the absolute path to the segments JSON file for a given event."""
    root = _get_project_root()
    return os.path.join(root, EVENTS_DATA_DIR, f'{event_slug}_segments.json')

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

def _get_summary_file_path(event_slug, segment_type, header, position):
    """Constructs the absolute path to a segment's summary Markdown file."""
    root = _get_project_root()
    event_tmp_dir = os.path.join(root, TMP_DIR, slugify(event_slug))
    # Ensure header is not empty for filename generation
    header_slug = slugify(header) if header else "no-header"
    type_slug = slugify(segment_type)
    return os.path.join(event_tmp_dir, f'{type_slug}_{header_slug}_{position}.md')

def _ensure_summary_dir_exists(event_slug):
    """Ensures the directory for an event's segment summaries exists."""
    root = _get_project_root()
    event_tmp_dir = os.path.join(root, TMP_DIR, slugify(event_slug))
    os.makedirs(event_tmp_dir, exist_ok=True)
    return event_tmp_dir

def load_segments(event_slug):
    """Loads segments for a specific event from its JSON file."""
    file_path = _get_segments_file_path(event_slug)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content:
            return []
        return json.loads(content)

def save_segments(event_slug, segments_list):
    """Saves segments for a specific event to its JSON file."""
    file_path = _get_segments_file_path(event_slug)
    # Ensure the directory for event segment files exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(segments_list, f, indent=4)

def get_segment_by_position(event_slug, position):
    """Retrieves a single segment for an event by its position."""
    segments = load_segments(event_slug)
    for segment in segments:
        if segment.get('position') == int(position):
            return segment
    return None

def load_summary_content(summary_file_path):
    """Loads the content of a summary file."""
    if not os.path.exists(summary_file_path):
        return ""
    with open(summary_file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_summary_content(summary_file_path, content):
    """Saves content to a summary file."""
    os.makedirs(os.path.dirname(summary_file_path), exist_ok=True)
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def delete_summary_file(summary_file_path):
    """Deletes a summary file if it exists."""
    if os.path.exists(summary_file_path):
        os.remove(summary_file_path)

def add_segment(event_slug, segment_data, summary_content):
    """Adds a new segment to an event."""
    segments = load_segments(event_slug)
    if any(s.get('position') == segment_data['position'] for s in segments):
        return False # Segment with this position already exists

    segment_data['summary_file'] = _get_summary_file_path(
        event_slug,
        segment_data.get('type', ''),
        segment_data.get('header', ''),
        segment_data['position']
    )
    segments.append(segment_data)
    segments.sort(key=lambda s: s['position']) # Keep segments sorted
    save_segments(event_slug, segments)
    save_summary_content(segment_data['summary_file'], summary_content)
    return True

def update_segment(event_slug, original_position, updated_data, summary_content):
    """Updates an existing segment for an event."""
    segments = load_segments(event_slug)
    found = False
    old_summary_file_path = None

    for i, segment in enumerate(segments):
        if segment.get('position') == int(original_position):
            found = True
            old_summary_file_path = segment.get('summary_file')

            # Check for position conflict if position is changed
            if updated_data['position'] != int(original_position) and \
               any(s.get('position') == updated_data['position'] and s.get('position') != int(original_position) for s in segments):
                return False # New position conflicts with another segment

            # Update segment data
            segments[i] = updated_data
            # Generate new summary file path based on potentially updated fields
            segments[i]['summary_file'] = _get_summary_file_path(
                event_slug,
                updated_data.get('type', ''),
                updated_data.get('header', ''),
                updated_data['position']
            )
            break

    if found:
        # Delete old summary file if its path changed
        new_summary_file_path = segments[i]['summary_file']
        if old_summary_file_path and old_summary_file_path != new_summary_file_path:
            delete_summary_file(old_summary_file_path)

        segments.sort(key=lambda s: s['position']) # Re-sort segments
        save_segments(event_slug, segments)
        save_summary_content(new_summary_file_path, summary_content)
        return True
    return False

def delete_segment(event_slug, position):
    """Deletes a segment and its associated summary file for an event."""
    segments = load_segments(event_slug)
    initial_len = len(segments)
    segment_to_delete = None

    for segment in segments:
        if segment.get('position') == int(position):
            segment_to_delete = segment
            break

    if segment_to_delete:
        segments = [s for s in segments if s.get('position') != int(position)]
        if len(segments) < initial_len:
            save_segments(event_slug, segments)
            delete_summary_file(segment_to_delete.get('summary_file', ''))
            return True
    return False

def delete_all_segments_for_event(event_name):
    """
    Deletes the segments JSON file and all associated summary Markdown files
    for a given event.
    """
    sluggified_event_name = slugify(event_name)
    segments_file_path = _get_segments_file_path(sluggified_event_name)
    
    # Load segments to get paths to summary files
    segments = load_segments(sluggified_event_name)
    for segment in segments:
        if 'summary_file' in segment:
            delete_summary_file(segment['summary_file'])

    # Delete the main segments JSON file
    if os.path.exists(segments_file_path):
        os.remove(segments_file_path)
        return True
    return False
