import os
import shutil

DATA_DIR = 'data'
EVENTS_DATA_SUBDIR = os.path.join(DATA_DIR, 'events')
TMP_DIR = 'includes/tmp'

# List of all primary data files to be deleted. prefs.json is excluded.
DATA_FILES = [
    'belts.json', 'belt_history.json', 'divisions.json', 
    'events.json', 'news.json', 'tagteams.json', 'wrestlers.json'
]

def get_project_root():
    """Helper function to get the project's root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def delete_all_league_data():
    """Deletes all user-generated data files and directories for a complete reset."""
    project_root = get_project_root()
    # 1. Delete individual data files
    for file_name in DATA_FILES:
        file_path = os.path.join(project_root, DATA_DIR, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error removing file {file_path}: {e}")

    # 2. Wipe and recreate the data/events subdirectory
    events_dir_path = os.path.join(project_root, EVENTS_DATA_SUBDIR)
    if os.path.exists(events_dir_path):
        try:
            shutil.rmtree(events_dir_path)
            os.makedirs(events_dir_path)
        except OSError as e:
            print(f"Error clearing directory {events_dir_path}: {e}")

    # 3. Wipe and recreate the includes/tmp directory
    delete_all_temporary_files()
            
    return True

def delete_all_temporary_files():
    """Deletes all generated summary files from the temporary directory."""
    project_root = get_project_root()
    tmp_dir_path = os.path.join(project_root, TMP_DIR)
    if os.path.exists(tmp_dir_path):
        try:
            shutil.rmtree(tmp_dir_path)
            os.makedirs(tmp_dir_path) # Recreate the empty directory
            return True
        except OSError as e:
            print(f"Error clearing directory {tmp_dir_path}: {e}")
            return False
    else:
        # If it doesn't exist, create it
        os.makedirs(tmp_dir_path)
        return True

