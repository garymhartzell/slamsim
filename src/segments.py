import json
import os
import re
import unicodedata
import uuid

# Base directories
DATA_DIR = 'data'
EVENTS_DATA_DIR = os.path.join(DATA_DIR, 'events')
INCLUDES_DIR = 'includes'
TMP_DIR = os.path.join(INCLUDES_DIR, 'tmp')

# File paths for static data (relative to project root)
WRESTLERS_FILE = os.path.join(DATA_DIR, 'wrestlers.json')
TAGTEAMS_FILE = os.path.join(DATA_DIR, 'tagteams.json')


def _get_project_root():
    """Returns the absolute path to the project root directory."""
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, os.pardir))


def _get_segments_file_path(event_slug):
    """Constructs the absolute path to the segments JSON file for a given event."""
    root = _get_project_root()
    return os.path.join(root, EVENTS_DATA_DIR, f'{event_slug}_segments.json')


def _get_matches_file_path(event_slug):
    """Constructs the absolute path to the matches JSON file for a given event."""
    root = _get_project_root()
    return os.path.join(root, EVENTS_DATA_DIR, f'{event_slug}_matches.json')


def _slugify(value):
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
    event_tmp_dir = os.path.join(root, TMP_DIR, _slugify(event_slug))
    # Ensure header is not empty for filename generation
    header_slug = _slugify(header) if header else "no-header"
    type_slug = _slugify(segment_type)
    return os.path.join(event_tmp_dir, f'{type_slug}_{header_slug}_{position}.md')


def _ensure_summary_dir_exists(event_slug):
    """Ensures the directory for an event's segment summaries exists."""
    root = _get_project_root()
    event_tmp_dir = os.path.join(root, TMP_DIR, _slugify(event_slug))
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


def load_matches(event_slug):
    """Loads match data for a specific event from its JSON file."""
    file_path = _get_matches_file_path(event_slug)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content:
            return []
        return json.loads(content)


def save_matches(event_slug, matches_list):
    """Saves match data for a specific event to its JSON file."""
    file_path = _get_matches_file_path(event_slug)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(matches_list, f, indent=4)


def get_segment_by_position(event_slug, position):
    """Retrieves a single segment for an event by its position."""
    segments = load_segments(event_slug)
    for segment in segments:
        if segment.get('position') == int(position):
            return segment
    return None


def get_match_by_id(event_slug, match_id):
    """Retrieves a single match by its match_id for a given event."""
    matches = load_matches(event_slug)
    for match in matches:
        if match.get('match_id') == match_id:
            return match
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


def load_active_wrestlers():
    """Loads active wrestlers from wrestlers.json."""
    root = _get_project_root()
    file_path = os.path.join(root, WRESTLERS_FILE)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        wrestlers = json.load(f)
    return [w for w in wrestlers if w.get('Status') == 'Active']


def load_active_tagteams():
    """Loads active tag teams from tagteams.json."""
    root = _get_project_root()
    file_path = os.path.join(root, TAGTEAMS_FILE)
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        tagteams = json.load(f)
    return [t for t in tagteams if t.get('Status') == 'Active']


def generate_match_display_string(sides):
    """Generates a readable display string for match participants."""
    side_strings = []
    for side in sides:
        if side.get('tagteam'):
            side_strings.append(side['tagteam'])
        else:
            side_strings.append(", ".join(side['members']))
    return " vs ".join(side_strings)


def validate_match_data(sides):
    """
    Validates match data based on specified rules:
    - Each match must have at least 2 sides.
    - Each side must have at least 1 entity.
    - If any side is more than one wrestler larger or smaller than another, show a warning.
    Returns a list of error/warning messages.
    """
    errors = []
    warnings = []

    if not sides or len(sides) < 2:
        errors.append("A match must have at least 2 sides.")
        return errors, warnings # Early exit if fundamental structure is missing

    for i, side in enumerate(sides):
        if not side.get('members'):
            errors.append(f"Side {i+1} must have at least one participant.")

    # Check for side size imbalance (only if no critical errors prevent size calculation)
    if not errors:
        member_counts = [len(side['members']) for side in sides]
        if member_counts:
            min_count = min(member_counts)
            max_count = max(member_counts)

            if max_count - min_count > 1:
                warnings.append("Warning: Some sides have significantly more or fewer participants than others.")

    return errors, warnings


def add_segment(event_slug, segment_data, summary_content, match_data=None):
    """Adds a new segment to an event. If it's a match, also adds match data."""
    segments = load_segments(event_slug)
    if any(s.get('position') == segment_data['position'] for s in segments):
        return False, "A segment with this position already exists." # Segment with this position already exists

    # Generate summary file path
    segment_data['summary_file'] = _get_summary_file_path(
        event_slug,
        segment_data.get('type', ''),
        segment_data.get('header', ''),
        segment_data['position']
    )

    if segment_data['type'] == 'Match' and match_data is not None:
        # Generate a unique match ID
        match_id = str(uuid.uuid4())
        segment_data['match_id'] = match_id
        segment_data['participants_display'] = match_data['participants_display']
        segment_data['sides'] = match_data['sides'] # Store simplified sides in segment data

        # Prepare full match data for separate storage
        full_match_data = {
            'match_id': match_id,
            'segment_position': segment_data['position'],
            'participants_display': match_data['participants_display'],
            'sides': match_data['sides'],
            'match_class': match_data.get('match_class', ''), # Placeholder for future
            'match_result': match_data.get('match_result', ''),
            'match_championship': match_data.get('match_championship', ''),
            'match_hidden': match_data.get('match_hidden', False),
            'match_time': match_data.get('match_time', ''),
        }
        _add_match(event_slug, full_match_data)
    else:
        # Remove match-specific fields if segment is not a match or no match_data provided
        segment_data.pop('match_id', None)
        segment_data.pop('participants_display', None)
        segment_data.pop('sides', None)

    segments.append(segment_data)
    segments.sort(key=lambda s: s['position'])  # Keep segments sorted
    save_segments(event_slug, segments)
    save_summary_content(segment_data['summary_file'], summary_content)
    return True, "Segment added successfully."


def _add_match(event_slug, match_data):
    """Internal function to add a new match to an event's matches file."""
    matches = load_matches(event_slug)
    matches.append(match_data)
    save_matches(event_slug, matches)


def update_segment(event_slug, original_position, updated_data, summary_content, match_data=None):
    """Updates an existing segment for an event. If it's a match, also updates match data."""
    segments = load_segments(event_slug)
    found = False
    old_summary_file_path = None
    old_match_id = None
    segment_index = -1

    for i, segment in enumerate(segments):
        if segment.get('position') == int(original_position):
            found = True
            segment_index = i
            old_summary_file_path = segment.get('summary_file')
            old_match_id = segment.get('match_id')
            break

    if not found:
        return False, f"Segment at position {original_position} not found."

    # Check for position conflict if position is changed
    if updated_data['position'] != int(original_position) and \
       any(s.get('position') == updated_data['position'] and s.get('position') != int(original_position) for s in segments):
        return False, f"New position '{updated_data['position']}' conflicts with another segment."

    # Handle match data if the segment is a match
    if updated_data['type'] == 'Match' and match_data is not None:
        if old_match_id:
            # Update existing match
            updated_data['match_id'] = old_match_id # Preserve existing match_id
            updated_data['participants_display'] = match_data['participants_display']
            updated_data['sides'] = match_data['sides']

            full_match_data = {
                'match_id': old_match_id,
                'segment_position': updated_data['position'], # Update position in match data as well
                'participants_display': match_data['participants_display'],
                'sides': match_data['sides'],
                'match_class': match_data.get('match_class', ''),
                'match_result': match_data.get('match_result', ''),
                'match_championship': match_data.get('match_championship', ''),
                'match_hidden': match_data.get('match_hidden', False),
                'match_time': match_data.get('match_time', ''),
            }
            _update_match(event_slug, old_match_id, full_match_data)
        else:
            # It became a match, add new match data
            match_id = str(uuid.uuid4())
            updated_data['match_id'] = match_id
            updated_data['participants_display'] = match_data['participants_display']
            updated_data['sides'] = match_data['sides']

            full_match_data = {
                'match_id': match_id,
                'segment_position': updated_data['position'],
                'participants_display': match_data['participants_display'],
                'sides': match_data['sides'],
                'match_class': match_data.get('match_class', ''),
                'match_result': match_data.get('match_result', ''),
                'match_championship': match_data.get('match_championship', ''),
                'match_hidden': match_data.get('match_hidden', False),
                'match_time': match_data.get('match_time', ''),
            }
            _add_match(event_slug, full_match_data)
    elif old_match_id:
        # Segment changed from Match to another type, delete associated match data
        _delete_match(event_slug, old_match_id)
        updated_data.pop('match_id', None)
        updated_data.pop('participants_display', None)
        updated_data.pop('sides', None)

    # Update segment data with new values (including potentially new match_id/display/sides)
    segments[segment_index] = updated_data
    # Generate new summary file path based on potentially updated fields
    segments[segment_index]['summary_file'] = _get_summary_file_path(
        event_slug,
        updated_data.get('type', ''),
        updated_data.get('header', ''),
        updated_data['position']
    )

    # Delete old summary file if its path changed
    new_summary_file_path = segments[segment_index]['summary_file']
    if old_summary_file_path and old_summary_file_path != new_summary_file_path:
        delete_summary_file(old_summary_file_path)

    segments.sort(key=lambda s: s['position'])  # Re-sort segments
    save_segments(event_slug, segments)
    save_summary_content(new_summary_file_path, summary_content)
    return True, "Segment updated successfully."


def _update_match(event_slug, match_id, updated_match_data):
    """Internal function to update an existing match in an event's matches file."""
    matches = load_matches(event_slug)
    found = False
    for i, match in enumerate(matches):
        if match.get('match_id') == match_id:
            matches[i] = updated_match_data
            found = True
            break
    if found:
        save_matches(event_slug, matches)
    return found


def delete_segment(event_slug, position):
    """Deletes a segment and its associated summary file and match data for an event."""
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
            
            # If it was a match, delete its associated match data
            if segment_to_delete.get('type') == 'Match' and segment_to_delete.get('match_id'):
                _delete_match(event_slug, segment_to_delete['match_id'])
            return True
    return False


def _delete_match(event_slug, match_id):
    """Internal function to delete a match from an event's matches file."""
    matches = load_matches(event_slug)
    initial_len = len(matches)
    matches = [m for m in matches if m.get('match_id') != match_id]
    if len(matches) < initial_len:
        save_matches(event_slug, matches)
        return True
    return False


def delete_all_segments_for_event(event_name):
    """
    Deletes the segments JSON file and all associated summary Markdown files
    and the matches JSON file for a given event.
    """
    sluggified_event_name = _slugify(event_name)
    segments_file_path = _get_segments_file_path(sluggified_event_name)
    matches_file_path = _get_matches_file_path(sluggified_event_name) # Path to matches file

    # Load segments to get paths to summary files and match IDs
    segments = load_segments(sluggified_event_name)
    for segment in segments:
        if 'summary_file' in segment:
            delete_summary_file(segment['summary_file'])

    # Delete the main segments JSON file
    if os.path.exists(segments_file_path):
        os.remove(segments_file_path)

    # Delete the matches JSON file
    if os.path.exists(matches_file_path):
        os.remove(matches_file_path)
        
    return True # Return True if segment file existed or if processing completes
