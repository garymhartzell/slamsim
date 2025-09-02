from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.events import load_events, get_event_by_name, add_event, update_event, delete_event
from src.segments import load_segments, load_summary_content, slugify, delete_all_segments_for_event # Import slugify and delete_all_segments_for_event
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/events')

STATUS_OPTIONS = ['Future', 'Past', 'Cancelled']

def _get_form_data(form):
    """Extracts event data from the form."""
    return {
        'Event_Name': form.get('event_name'),
        'Subtitle': form.get('subtitle', ''),
        'Status': form.get('status'),
        'Date': form.get('date'),
        'Venue': form.get('venue', ''),
        'Location': form.get('location', ''),
        'Broadcasters': form.get('broadcasters', '')
    }

@events_bp.route('/')
def list_events():
    """Displays a list of all events."""
    events = load_events()
    return render_template('events/list.html', events=events)

@events_bp.route('/create', methods=['GET', 'POST'])
def create_event():
    """Handles event creation."""
    if request.method == 'POST':
        event_data = _get_form_data(request.form)
        if not event_data['Event_Name'] or not event_data['Status'] or not event_data['Date']:
            flash('Event Name, Status, and Date are required.', 'danger')
            return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS)

        # Basic date validation for format (can be expanded)
        try:
            datetime.strptime(event_data['Date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS)

        if add_event(event_data):
            flash(f"Event '{event_data['Event_Name']}' created successfully!", 'success')
            return redirect(url_for('events.list_events'))
        else:
            flash(f"Event with name '{event_data['Event_Name']}' already exists.", 'danger')

    return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS)

@events_bp.route('/edit/<string:event_name>', methods=['GET', 'POST'])
def edit_event(event_name):
    """Handles event editing."""
    event = get_event_by_name(event_name)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('events.list_events'))

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        if not updated_data['Event_Name'] or not updated_data['Status'] or not updated_data['Date']:
            flash('Event Name, Status, and Date are required.', 'danger')
            return render_template('events/form.html', event=event, status_options=STATUS_OPTIONS)

        try:
            datetime.strptime(updated_data['Date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('events/form.html', event=event, status_options=STATUS_OPTIONS)

        if update_event(event_name, updated_data):
            flash(f"Event '{updated_data['Event_Name']}' updated successfully!", 'success')
            return redirect(url_for('events.list_events'))
        else:
            flash(f"Failed to update event '{event_name}'. New name might conflict or event not found.", 'danger')
            # If update fails, re-render form with current data (could be conflicting new name)
            return render_template('events/form.html', event=updated_data, status_options=STATUS_OPTIONS, original_name=event_name)

    return render_template('events/form.html', event=event, status_options=STATUS_OPTIONS, original_name=event_name)

@events_bp.route('/view/<string:event_name>')
def view_event(event_name):
    """Displays details of a single event and its segments."""
    event = get_event_by_name(event_name)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('events.list_events'))

    segments = load_segments(slugify(event_name)) # Use sluggified name
    # Load summary content for each segment to display directly
    for segment in segments:
        if segment.get('summary_file'):
            segment['summary_content'] = load_summary_content(segment['summary_file'])
        else:
            segment['summary_content'] = ''
    segments.sort(key=lambda s: s['position']) # Ensure segments are sorted by position

    return render_template('events/view.html', event=event, segments=segments)

@events_bp.route('/delete/<string:event_name>', methods=['POST'])
def delete_event_route(event_name):
    """Handles event deletion and also deletes associated segment files."""
    if delete_event(event_name):
        # Also attempt to delete all segments and their summary files for this event
        delete_all_segments_for_event(event_name)
        flash(f"Event '{event_name}' and its segments deleted successfully!", 'success')
    else:
        flash(f"Failed to delete event '{event_name}'. Event not found.", 'danger')
    return redirect(url_for('events.list_events'))
def delete_event_route(event_name):
    """Handles event deletion."""
    if delete_event(event_name):
        flash(f"Event '{event_name}' deleted successfully!", 'success')
    else:
        flash(f"Failed to delete event '{event_name}'. Event not found.", 'danger')
    return redirect(url_for('events.list_events'))
