import json
import os

EVENTS_FILE_RELATIVE_TO_ROOT = 'data/events.json'

def _get_events_file_path():
    """Constructs the absolute path to the events JSON file."""
    # Assumes the script is run from the project root or src directory
    current_dir = os.path.dirname(__file__)
    # Go up one level from 'src' to the project root, then into 'data'
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
    return os.path.join(project_root, EVENTS_FILE_RELATIVE_TO_ROOT)

def load_events():
    """Loads events from the JSON file."""
    file_path = _get_events_file_path()
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        # Check if file is empty before loading JSON
        content = f.read()
        if not content:
            return []
        f.seek(0) # Reset file pointer to the beginning if content was read
        return json.loads(content)

def save_events(events_list):
    """Saves events to the JSON file."""
    file_path = _get_events_file_path()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(events_list, f, indent=4)

def get_event_by_name(event_name):
    """Retrieves a single event by its name."""
    events = load_events()
    for event in events:
        if event.get('Event_Name') == event_name:
            return event
    return None

def add_event(event_data):
    """Adds a new event to the list."""
    events = load_events()
    if get_event_by_name(event_data['Event_Name']):
        return False # Event with this name already exists
    events.append(event_data)
    save_events(events)
    return True

def update_event(original_name, updated_data):
    """Updates an existing event."""
    events = load_events()
    for i, event in enumerate(events):
        if event.get('Event_Name') == original_name:
            # Check if name changed and new name already exists (and it's not the same event)
            if updated_data['Event_Name'] != original_name and get_event_by_name(updated_data['Event_Name']):
                return False # New name conflicts with another existing event
            events[i] = updated_data
            save_events(events)
            return True
    return False # Event not found

def delete_event(event_name):
    """Deletes an event by its name."""
    events = load_events()
    initial_len = len(events)
    events = [event for event in events if event.get('Event_Name') != event_name]
    if len(events) < initial_len:
        save_events(events)
        return True
    return False # Event not found
