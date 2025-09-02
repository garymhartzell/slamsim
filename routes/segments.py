from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.segments import (
    load_segments, get_segment_by_position, add_segment, update_segment, delete_segment,
    load_summary_content, slugify, delete_all_segments_for_event # Added delete_all_segments_for_event (though not used here directly)
)
from src.events import get_event_by_name # To check if event exists

segments_bp = Blueprint('segments', __name__, url_prefix='/events/<string:event_slug>/segments')

SEGMENT_TYPE_OPTIONS = ["Match", "Promo", "Interview", "In-ring", "Brawl"]

def _get_segment_form_data(form):
    """Extracts segment data from the form."""
    match_hidden = form.get('match_hidden') == 'on'
    position_str = form.get('position')
    position = int(position_str) if position_str and position_str.isdigit() else None

    return {
        'position': position,
        'type': form.get('type'),
        'header': form.get('header', ''),
        'participants': form.get('participants', ''),
        'match_result': form.get('match_result', ''),
        'match_time': form.get('match_time', ''),
        'match_championship': form.get('match_championship', ''),
        'match_hidden': match_hidden,
    }

def _validate_segment_data(segment_data):
    """Performs basic validation on segment data."""
    errors = []
    if segment_data['position'] is None:
        errors.append("Position is required and must be an integer.")
    if not segment_data['type']:
        errors.append("Type is required.")
    if segment_data['type'] not in SEGMENT_TYPE_OPTIONS:
        errors.append(f"Invalid segment type: {segment_data['type']}.")
    # Add more specific validation for match_time format if needed later
    return errors

@segments_bp.route('/create', methods=['GET', 'POST'])
def create_segment(event_slug):
    """Handles segment creation for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = slugify(event_slug) # Sluggify the event name for file operations

    summary_content = ""
    if request.method == 'POST':
        segment_data = _get_segment_form_data(request.form)
        summary_content = request.form.get('summary_text', '')

        errors = _validate_segment_data(segment_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('segments/form.html', event_slug=event_slug, segment={},
                                   segment_type_options=SEGMENT_TYPE_OPTIONS,
                                   summary_content=summary_content)

        if add_segment(sluggified_event_name, segment_data, summary_content): # Use sluggified name
            flash(f"Segment '{segment_data['header']}' (Position: {segment_data['position']}) added successfully!", 'success')
            return redirect(url_for('events.view_event', event_name=event_slug))
        else:
            flash(f"Failed to add segment. A segment with position '{segment_data['position']}' might already exist.", 'danger')

    return render_template('segments/form.html', event_slug=event_slug, segment={},
                           segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=summary_content)

@segments_bp.route('/edit/<int:position>', methods=['GET', 'POST'])
def edit_segment(event_slug, position):
    """Handles segment editing for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = slugify(event_slug) # Sluggify the event name for file operations

    segment = get_segment_by_position(sluggified_event_name, position) # Use sluggified name
    if not segment:
        flash(f"Segment at position {position} not found for event '{event_slug}'.", 'danger')
        return redirect(url_for('events.view_event', event_name=event_slug))

    summary_content = load_summary_content(segment.get('summary_file', ''))

    if request.method == 'POST':
        updated_data = _get_segment_form_data(request.form)
        new_summary_content = request.form.get('summary_text', '')

        errors = _validate_segment_data(updated_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('segments/form.html', event_slug=event_slug, segment=updated_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS,
                                   summary_content=new_summary_content, original_position=position)

        if update_segment(sluggified_event_name, position, updated_data, new_summary_content): # Use sluggified name
            flash(f"Segment '{updated_data['header']}' (Position: {updated_data['position']}) updated successfully!", 'success')
            return redirect(url_for('events.view_event', event_name=event_slug))
        else:
            flash(f"Failed to update segment at position {position}. New position might conflict or segment not found.", 'danger')
            # Re-render with updated_data if update failed due to conflict
            return render_template('segments/form.html', event_slug=event_slug, segment=updated_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS,
                                   summary_content=new_summary_content, original_position=position)

    return render_template('segments/form.html', event_slug=event_slug, segment=segment,
                           segment_type_options=SEGMENT_TYPE_OPTIONS,
                           summary_content=summary_content, original_position=position)

@segments_bp.route('/delete/<int:position>', methods=['POST'])
def delete_segment_route(event_slug, position):
    """Handles segment deletion for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = slugify(event_slug) # Sluggify the event name for file operations

    if delete_segment(sluggified_event_name, position): # Use sluggified name
        flash(f"Segment at position {position} deleted successfully!", 'success')
    else:
        flash(f"Failed to delete segment at position {position}. Segment not found.", 'danger')
    return redirect(url_for('events.view_event', event_name=event_slug))
