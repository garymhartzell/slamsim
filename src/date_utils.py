import datetime
from src.prefs import load_preferences

def get_current_working_date():
    """
    Returns the current working date based on preferences.
    If game_date_mode is 'real-time', returns today's date.
    If game_date_mode is 'latest-event-date', returns the date stored in 'game_date' preference.
    """
    prefs = load_preferences()
    game_date_mode = prefs.get('game_date_mode', 'real-time')
    
    if game_date_mode == 'real-time':
        return datetime.date.today()
    elif game_date_mode == 'latest-event-date':
        game_date_str = prefs.get('game_date')
        if game_date_str:
            try:
                return datetime.date.fromisoformat(game_date_str)
            except ValueError:
                # Fallback if stored game_date is malformed
                return datetime.date.today()
        else:
            # Fallback if game_date is not set in prefs
            return datetime.date.today()
    else:
        # Default fallback
        return datetime.date.today()
