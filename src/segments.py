import json
import os
import re
import unicodedata
import uuid

from .prefs import load_preferences
from .wrestlers import load_wrestlers
from .tagteams import load_tagteams

# Base directories
DATA_DIR = 'data'
EVENTS_DATA_DIR = os.path.join(DATA_DIR, 'events')
INCLUDES_DIR = 'includes'
TMP_DIR = os.path.join(INCLUDES_DIR, 'tmp')

# File paths for static data (relative to project root)
WRESTLERS_FILE = os.path.join(DATA_DIR, 'wrestlers.json')
TAGTEAMS_FILE = os.path.join(DATA_DIR, 'tagteams.json')


def _classify_match(sides):
    """
    Classifies a match based on its sides array.
    - 'battle_royal': 10+ sides, each with exactly one wrestler.
    - 'singles': 2–9 sides, each with exactly one wrestler.
    - 'tag': any match where any side has 2+ wrestlers.
    - 'other': fallback for unclassifiable formats.
    """
    num_sides = len(sides)
    all_single_wrestlers = all(len(side) == 1 for side in sides)
    any_side_has_multiple_wrestlers = any(len(side) > 1 for side in sides)

    if all_single_wrestlers and num_sides >= 10:
        return "battle_royal"
    elif all_single_wrestlers and 2 <= num_sides <= 9:
        return "singles"
    elif any_side_has_multiple_wrestlers:
        return "tag"
    else:
        # This covers cases like 1-on-X handicap or other complex formats
        return "other"

def _get_all_wrestlers_involved(sides):
    """Extracts all unique wrestler names involved in the match from the sides structure."""
    wrestlers = set()
    for side in sides:
        for participant in side:
            wrestlers.add(participant)
    return list(wrestlers)

def _get_all_tag_teams_involved(sides, all_tagteams_data):
    """
    Identifies tag teams from the provided `sides` that match known tag teams in `all_tagteams_data`.
    A team is considered involved if its members are fully present in any single side of the match.
    """
    teams = set()
    
    # Create a map of team name to a set of its members for efficient lookup
    team_member_sets = {}
    for team_data in all_tagteams_data:
        team_name = team_data.get('Name')
        members_str = team_data.get('Members', '')
        if team_name and members_str:
            team_member_sets[team_name] = set(members_str.split('|'))
    
    for side in sides:
        side_members_set = set(side)
        for team_name, members_set in team_member_sets.items():
            # Check if all members of a known team are present in the current side
            # and that the team has more than one member (to avoid single wrestlers being seen as teams)
            if members_set.issubset(side_members_set) and len(members_set) > 1:
                teams.add(team_name)
    
    return list(teams)

def _prepare_match_data_for_storage(match_data_input, all_wrestlers_data, all_tagteams_data):
    """
    Prepares match data for storage, including classifying the match,
    initializing individual and team results, and setting default options.
    """
    prepared_match_data = match_data_input.copy()
    sides = prepared_match_data.get('sides', [])

    if "match_class" not in prepared_match_data:
        prepared_match_data["match_class"] = _classify_match(sides)

    all_wrestlers_in_match = _get_all_wrestlers_involved(sides)
    all_teams_in_match = _get_all_tag_teams_involved(sides, all_tagteams_data)

    # Initialize or update individual results
    if "individual_results" not in prepared_match_data:
        prepared_match_data["individual_results"] = {}
    
    # Add new wrestlers to results, defaulting to "No Contest"
    for wrestler in all_wrestlers_in_match:
        if wrestler not in prepared_match_data["individual_results"]:
            prepared_match_data["individual_results"][wrestler] = "No Contest"
    
    # Remove wrestlers from results who are no longer in the match
    current_wrestler_results_keys = list(prepared_match_data["individual_results"].keys())
    for wrestler_key in current_wrestler_results_keys:
        if wrestler_key not in all_wrestlers_in_match:
            del prepared_match_data["individual_results"][wrestler_key]

    # Initialize or update team results
    if "team_results" not in prepared_match_data:
        prepared_match_data["team_results"] = {}
    
    # Add new teams to results, defaulting to "No Contest"
    for team in all_teams_in_match:
        if team not in prepared_match_data["team_results"]:
            prepared_match_data["team_results"][team] = "No Contest"

    # Remove teams from results who are no longer in the match
    current_team_results_keys = list(prepared_match_data["team_results"].keys())
    for team_key in current_team_results_keys:
        if team_key not in all_teams_in_match:
            del prepared_match_data["team_results"][team_key]

    # Initialize winning side index
    if "winning_side_index" not in prepared_match_data:
        prepared_match_data["winning_side_index"] = -1 # -1 means no winning side selected

    # Initialize sync toggle
    if "sync_teams_to_individuals" not in prepared_match_data:
        prepared_match_data["sync_teams_to_individuals"] = True # Default to syncing

    return prepared_match_data

def _sync_team_results_to_individuals(match_results, all_tagteams_data):
    """
    Synchronizes team results to individual members, respecting existing manual overrides
    (i.e., only overwrites if individual result is "No Contest" or missing).
    """
    if not match_results.get("sync_teams_to_individuals", True):
        return match_results # Skip if syncing is disabled

    team_results = match_results.get("team_results", {})
    individual_results = match_results.get("individual_results", {})
    
    team_members_map = {
        team_data['Name']: team_data['Members'].split('|')
        for team_data in all_tagteams_data if 'Name' in team_data and 'Members' in team_data
    }

    for team_name, result in team_results.items():
        if team_name in team_members_map:
            for member in team_members_map[team_name]:
                # Only sync if the individual result is "No Contest" or not set
                if individual_results.get(member) in ["No Contest", None]:
                    individual_results[member] = result
    
    match_results["individual_results"] = individual_results
    return match_results

def _validate_match_structure(sides):
    """
    Validates the structure of match sides, checking for empty sides or unbalanced teams.
    Returns a list of warning messages.
    """
    warnings = []
    num_sides = len(sides)
    if num_sides == 0:
        warnings.append("Match has no sides specified.")
        return warnings

    side_lengths = [len(side) for side in sides]
    
    if any(length == 0 for length in side_lengths):
        warnings.append("Some sides have no wrestlers specified.")
        
    if len(set(side_lengths)) > 1:
        min_members = min(side_lengths)
        max_members = max(side_lengths)
        warnings.append(f"Match sides appear unbalanced (e.g., sides have {min_members} to {max_members} wrestlers). Review match structure.")

    return warnings

def _validate_result_completeness(match_results, sides, all_wrestlers_in_match, all_teams_in_match, all_tagteams_data):
    """
    Validates the completeness and consistency of match results.
    Returns a list of warning messages.
    """
    warnings = []
    individual_results = match_results.get("individual_results", {})
    team_results = match_results.get("team_results", {})
    winning_side_index = match_results.get("winning_side_index")

    # Check if all participants have a result
    valid_results = ["Win", "Loss", "Draw", "No Contest"]
    for wrestler in all_wrestlers_in_match:
        if wrestler not in individual_results or individual_results[wrestler] not in valid_results:
            warnings.append(f"Result missing or invalid for wrestler: {wrestler}")
    
    for team in all_teams_in_match:
        if team not in team_results or team_results[team] not in valid_results:
            warnings.append(f"Result missing or invalid for team: {team}")

    # Check consistency with winning side, if one is selected
    if winning_side_index is not None and winning_side_index != -1 and 0 <= winning_side_index < len(sides):
        winning_side_members = set(sides[winning_side_index])
        
        # Check individuals on winning side
        for wrestler in winning_side_members:
            if individual_results.get(wrestler) != "Win":
                warnings.append(f"Wrestler '{wrestler}' on declared winning side has result '{individual_results.get(wrestler, 'N/A')}' instead of 'Win'.")
        
        # Check individuals on non-winning sides
        for i, side in enumerate(sides):
            if i != winning_side_index:
                for wrestler in side:
                    if individual_results.get(wrestler) == "Win":
                        warnings.append(f"Wrestler '{wrestler}' on a non-winning side has result 'Win'.")
        
        # Check consistency for tag teams
        team_members_map = {
            team_data['Name']: set(team_data.get('Members', '').split('|'))
            for team_data in all_tagteams_data if 'Name' in team_data and 'Members' in team_data
        }
        
        for team_name in all_teams_in_match:
            if team_name in team_members_map:
                members_of_this_team = team_members_map[team_name]
                # A team is on the winning side if ALL its members are on the winning side
                is_team_on_winning_side = members_of_this_team.issubset(winning_side_members)
                
                if is_team_on_winning_side:
                    if team_results.get(team_name) != "Win":
                        warnings.append(f"Team '{team_name}' (whose members are all on the winning side) has result '{team_results.get(team_name, 'N/A')}' instead of 'Win'.")
                else:
                    if team_results.get(team_name) == "Win":
                        warnings.append(f"Team '{team_name}' (whose members are not all on the winning side) has result 'Win'.")

    return warnings

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


def validate_match_data(sides, match_results=None):
    """
    Validates match data based on specified rules, including structural and result completeness.
    Returns a list of errors and warnings.
    """
    errors = []
    warnings = []

    if not sides or len(sides) < 2:
        errors.append("A match must have at least 2 sides.")
        return errors, warnings # Early exit if fundamental structure is missing

    for i, side in enumerate(sides):
        if not side: # Check if the side list itself is empty
            errors.append(f"Side {i+1} must have at least one participant.")

    # Perform structural validation (e.g., unbalanced sides)
    warnings.extend(_validate_match_structure(sides))

    # Perform result completeness validation if match_results are provided
    if match_results:
        all_tagteams_data = load_tagteams()
        all_wrestlers_in_match = _get_all_wrestlers_involved(sides)
        all_teams_in_match = _get_all_tag_teams_involved(sides, all_tagteams_data)
        warnings.extend(_validate_result_completeness(match_results, sides, all_wrestlers_in_match, all_teams_in_match, all_tagteams_data))

    return errors, warnings


def add_segment(event_slug, segment_data, summary_content, match_data=None):
    """Adds a new segment to an event. If it's a match, also adds match data."""
    segments = load_segments(event_slug)
    if any(s.get('position') == segment_data['position'] for s in segments):
        return False, "A segment with this position already exists."

    # Generate summary file path
    segment_data['summary_file'] = _get_summary_file_path(
        event_slug,
        segment_data.get('type', ''),
        segment_data.get('header', ''),
        segment_data['position']
    )

    if segment_data['type'] == 'Match' and match_data is not None:
        # Load necessary data for classification and result preparation
        all_wrestlers_data = load_wrestlers()
        all_tagteams_data = load_tagteams()

        # Prepare match data (classify, initialize results)
        processed_match_data = _prepare_match_data_for_storage(match_data, all_wrestlers_data, all_tagteams_data)
        
        # Sync team results to individuals if enabled
        processed_match_data = _sync_team_results_to_individuals(processed_match_data, all_tagteams_data)

        # Validate the processed match data
        errors, warnings = validate_match_data(processed_match_data.get('sides', []), processed_match_data)
        if errors:
            # If there are errors, do not add the segment
            raise ValueError(f"Match data validation failed: {', '.join(errors)}")
        if warnings:
            processed_match_data['warnings'] = warnings
        else:
            processed_match_data.pop('warnings', None) # Remove warnings if none exist

        # Generate a unique match ID
        match_id = str(uuid.uuid4())
        segment_data['match_id'] = match_id
        segment_data['participants_display'] = processed_match_data['participants_display']
        segment_data['sides'] = processed_match_data['sides'] # Store simplified sides in segment data

        # Store the full processed match data separately
        full_match_data_to_save = processed_match_data.copy()
        full_match_data_to_save['match_id'] = match_id
        full_match_data_to_save['segment_position'] = segment_data['position']
        
        _add_match(event_slug, full_match_data_to_save)
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
        # Load necessary data for classification and result preparation
        all_wrestlers_data = load_wrestlers()
        all_tagteams_data = load_tagteams()

        # Prepare match data (classify, initialize results)
        # Use existing match_id if present in match_data to ensure continuity
        processed_match_data = _prepare_match_data_for_storage(match_data, all_wrestlers_data, all_tagteams_data)
        
        # Sync team results to individuals if enabled
        processed_match_data = _sync_team_results_to_individuals(processed_match_data, all_tagteams_data)

        # Validate the processed match data
        errors, warnings = validate_match_data(processed_match_data.get('sides', []), processed_match_data)
        if errors:
            raise ValueError(f"Match data validation failed: {', '.join(errors)}")
        if warnings:
            processed_match_data['warnings'] = warnings
        else:
            processed_match_data.pop('warnings', None) # Remove warnings if none exist


        if old_match_id:
            # Update existing match
            updated_data['match_id'] = old_match_id # Preserve existing match_id
            updated_data['participants_display'] = processed_match_data['participants_display']
            updated_data['sides'] = processed_match_data['sides']

            full_match_data_to_save = processed_match_data.copy()
            full_match_data_to_save['match_id'] = old_match_id
            full_match_data_to_save['segment_position'] = updated_data['position'] # Update position in match data as well
            
            _update_match(event_slug, old_match_id, full_match_data_to_save)
        else:
            # It became a match, add new match data
            match_id = str(uuid.uuid4())
            updated_data['match_id'] = match_id
            updated_data['participants_display'] = processed_match_data['participants_display']
            updated_data['sides'] = processed_match_data['sides']

            full_match_data_to_save = processed_match_data.copy()
            full_match_data_to_save['match_id'] = match_id
            full_match_data_to_save['segment_position'] = updated_data['position']
            
            _add_match(event_slug, full_match_data_to_save)
    elif old_match_id:
        # Segment changed from Match to another type, delete associated match data
        _delete_match(event_slug, old_match_id)
        # Ensure match-specific fields are removed from the segment data itself
        updated_data.pop('match_id', None)
        updated_data.pop('participants_display', None)
        updated_data.pop('sides', None)

    # Update segment data with new values (including potentially new match_id/display/sides/warnings)
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
