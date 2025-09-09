from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.events import load_events, get_event_by_name, add_event, update_event, delete_event
from src.segments import load_segments, get_match_by_id, _get_all_wrestlers_involved, _get_all_tag_teams_involved, _slugify, delete_all_segments_for_event, load_summary_content
from src.wrestlers import update_wrestler_record
from src.tagteams import load_tagteams, update_tagteam_record, get_tagteam_by_name
from src.belts import get_belt_by_name, process_championship_change, update_reign_in_history, load_history_for_belt
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/events')

STATUS_OPTIONS = ['Future', 'Past', 'Cancelled']

def _get_form_data(form):
    """Extracts event data from the form."""
    return {
        'Event_Name': form.get('event_name'), 'Subtitle': form.get('subtitle', ''),
        'Status': form.get('status'), 'Date': form.get('date'),
        'Venue': form.get('venue', ''), 'Location': form.get('location', ''),
        'Broadcasters': form.get('broadcasters', ''),
        'Finalized': form.get('finalized', 'false').lower() == 'true'
    }

@events_bp.route('/')
def list_events():
    """Displays a list of all events, sorted by most recent."""
    events = sorted(load_events(), key=lambda e: e.get('Date', '0000-00-00'), reverse=True)
    return render_template('events/list.html', events=events)

@events_bp.route('/create', methods=['GET', 'POST'])
def create_event():
    """Handles event creation."""
    if request.method == 'POST':
        event_data = _get_form_data(request.form)
        if not all([event_data['Event_Name'], event_data['Status'], event_data['Date']]):
            flash('Event Name, Status, and Date are required.', 'danger')
            return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS, segments=[])

        try:
            datetime.strptime(event_data['Date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('events/form.html', event=event_data, status_options=STATUS_OPTIONS, segments=[])

        if add_event(event_data):
            flash(f"Event '{event_data['Event_Name']}' created successfully! You can now add segments.", 'success')
            return redirect(url_for('events.edit_event', event_name=event_data['Event_Name']))
        else:
            flash(f"Event with name '{event_data['Event_Name']}' already exists.", 'danger')
            return render_template('events/form.html', event=event_data, status_options=STATUS_OPTIONS, segments=[])

    return render_template('events/form.html', event={}, status_options=STATUS_OPTIONS, segments=[])

@events_bp.route('/edit/<string:event_name>', methods=['GET', 'POST'])
def edit_event(event_name):
    """Handles event editing and segment management."""
    event = get_event_by_name(event_name)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('events.list_events'))
    
    sluggified_name = _slugify(event_name)
    segments = sorted(load_segments(sluggified_name), key=lambda s: s.get('position', 0))

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        updated_data['Finalized'] = event.get('Finalized', False)
        
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
            return redirect(url_for('events.edit_event', event_name=updated_data['Event_Name']))
        else:
            flash(f"Failed to update event. New name might conflict.", 'danger')
            return render_template('events/form.html', event=updated_data, segments=segments, status_options=STATUS_OPTIONS, original_name=event_name)
    
    return render_template('events/form.html', event=event, segments=segments, status_options=STATUS_OPTIONS, original_name=event_name)

@events_bp.route('/view/<string:event_name>')
def view_event(event_name):
    """Displays details of a single event and its segments (read-only)."""
    event = get_event_by_name(event_name)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('events.list_events'))

    segments = load_segments(_slugify(event_name))
    for segment in segments:
        if segment.get('summary_file'):
            segment['summary_content'] = load_summary_content(segment['summary_file'])
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

@events_bp.route('/finalize/<string:event_name>', methods=['POST'])
def finalize_event(event_name):
    """Finalizes an event, updating records and championships."""
    event = get_event_by_name(event_name)
    if not event or event.get('Finalized'):
        flash('Event not found or already finalized.', 'warning')
        return redirect(url_for('events.list_events'))

    segments = load_segments(_slugify(event_name))
    all_tagteams = load_tagteams()

    for segment in segments:
        if segment.get('type') == 'Match' and segment.get('match_id'):
            match = get_match_by_id(_slugify(event_name), segment['match_id'])
            if not match: continue

            # Update records for tag team members first
            all_teams_in_match = _get_all_tag_teams_involved(match.get('sides', []), all_tagteams)
            for team_name in all_teams_in_match:
                team_result = match['team_results'].get(team_name)
                if team_result:
                    update_tagteam_record(team_name, team_result)
                    team_data = get_tagteam_by_name(team_name)
                    if team_data and team_data.get('Members'):
                        for member_name in team_data['Members'].split('|'):
                            update_wrestler_record(member_name, 'tag', team_result)
            
            # Update records for singles wrestlers
            all_wrestlers_in_match = _get_all_wrestlers_involved(match.get('sides', []))
            for wrestler_name in all_wrestlers_in_match:
                 if match.get('match_class') == 'singles':
                    result = match['individual_results'].get(wrestler_name)
                    if result:
                        update_wrestler_record(wrestler_name, 'singles', result)

            # Process championship changes
            belt_name = match.get('match_championship')
            if belt_name:
                belt = get_belt_by_name(belt_name)
                winning_side_idx = match.get('winning_side_index', -1)
                if belt and belt['Status'] == 'Active' and winning_side_idx != -1:
                    winning_side = match['sides'][winning_side_idx]
                    winner_name = None
                    if belt['Holder_Type'] == 'Singles' and len(winning_side) == 1:
                        winner_name = winning_side[0]
                    elif belt['Holder_Type'] == 'Tag-Team':
                        winning_teams = _get_all_tag_teams_involved([winning_side], all_tagteams)
                        if winning_teams: winner_name = winning_teams[0]

                    if winner_name and belt.get('Current_Holder') != winner_name:
                        process_championship_change(belt, winner_name, event['Date'])
                    elif winner_name and belt.get('Current_Holder') == winner_name:
                        history = load_history_for_belt(belt['ID'])
                        for reign in history:
                            if reign.get('Champion_Name') == belt['Current_Holder'] and not reign.get('Date_Lost'):
                                reign['Defenses'] = reign.get('Defenses', 0) + 1
                                update_reign_in_history(reign['Reign_ID'], reign)
                                break
    
    event['Finalized'] = True
    update_event(event_name, event)
    flash(f"Event '{event_name}' has been finalized and records updated!", 'success')
    return redirect(url_for('events.edit_event', event_name=event_name))

