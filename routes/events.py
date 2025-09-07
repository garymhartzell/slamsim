from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.events import load_events, get_event_by_name, add_event, update_event, delete_event
from src.segments import load_segments, _slugify, delete_all_segments_for_event
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
        if not all([event_data['Event_Name'], event_data['Status'], event_data['Date']]):
            flash('Event Name, Status, and Date are required.', 'danger')
            return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS)

        try:
            datetime.strptime(event_data['Date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('events/form.html', event=event_data, status_options=STATUS_OPTIONS)

        if add_event(event_data):
            flash(f"Event '{event_data['Event_Name']}' created successfully! You can now add segments.", 'success')
            return redirect(url_for('events.edit_event', event_name=event_data['Event_Name']))
        else:
            flash(f"Event with name '{event_data['Event_Name']}' already exists.", 'danger')
            return render_template('events/form.html', event=event_data, status_options=STATUS_OPTIONS)

    return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS, segments=[])

@events_bp.route('/edit/<string:event_name>', methods=['GET', 'POST'])
def edit_event(event_name):
    """Handles event editing and segment management."""
    event = get_event_by_name(event_name)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('events.list_events'))

    # Load segments to display on the edit page
    sluggified_name = _slugify(event_name)
    segments = load_segments(sluggified_name)

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        if not all([updated_data['Event_Name'], updated_data['Status'], updated_data['Date']]):
            flash('Event Name, Status, and Date are required.', 'danger')
            return render_template('events/form.html', event=event, segments=segments, status_options=STATUS_OPTIONS, original_name=event_name)

        try:
            datetime.strptime(updated_data['Date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('events/form.html', event=updated_data, segments=segments, status_options=STATUS_OPTIONS, original_name=event_name)

        if update_event(event_name, updated_data):
            flash(f"Event '{updated_data['Event_Name']}' updated successfully!", 'success')
            # If name changes, redirect to the new edit URL
            return redirect(url_for('events.edit_event', event_name=updated_data['Event_Name']))
        else:
            flash(f"Failed to update event. New name might conflict.", 'danger')
            return render_template('events/form.html', event=updated_data, segments=segments, status_options=STATUS_OPTIONS, original_name=event_name)
    
    # GET request
    return render_template('events/form.html', event=event, segments=segments, status_options=STATUS_OPTIONS, original_name=event_name)

@events_bp.route('/view/<string:event_name>')
def view_event(event_name):
    """Displays details of a single event and its segments (read-only)."""
    event = get_event_by_name(event_name)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('events.list_events'))

    segments = load_segments(_slugify(event_name))
    segments.sort(key=lambda s: s.get('position', 0))

    return render_template('events/view.html', event=event, segments=segments)

@events_bp.route('/delete/<string:event_name>', methods=['POST'])
def delete_event_route(event_name):
    """Handles event deletion and also deletes associated segment files."""
    if delete_event(event_name):
        delete_all_segments_for_event(event_name)
        flash(f"Event '{event_name}' and its segments deleted successfully!", 'success')
    else:
        flash(f"Failed to delete event '{event_name}'.", 'danger')
    return redirect(url_for('events.list_events'))

