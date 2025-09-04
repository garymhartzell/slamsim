from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.segments import (
    load_segments, get_segment_by_position, add_segment, update_segment, delete_segment,
    load_summary_content, _slugify, delete_all_segments_for_event,
    load_active_wrestlers, load_active_tagteams, get_match_by_id,
    generate_match_display_string, validate_match_data
)
from src.events import get_event_by_name  # To check if event exists
import json

segments_bp = Blueprint('segments', __name__, url_prefix='/events/<string:event_slug>/segments')

SEGMENT_TYPE_OPTIONS = ["Match", "Promo", "Interview", "In-ring", "Brawl"]


def _get_segment_form_data(form):
    """Extracts segment data from the form, including new match participant data."""
    position_str = form.get('position')
    position = int(position_str) if position_str and position_str.isdigit() else None
    
    segment_type = form.get('type')
    header = form.get('header', '')
    summary_text = form.get('summary_text', '')

    segment_data = {
        'position': position,
        'type': segment_type,
        'header': header,
        # summary_text is handled separately
    }

    match_details = None
    if segment_type == 'Match':
        match_sides_json = form.get('match_sides_json', '[]')
        match_sides = json.loads(match_sides_json)
        participants_display = form.get('participants_display', '')
        
        match_details = {
            'participants_display': participants_display,
            'sides': match_sides,
            'match_result': form.get('match_result', ''),
            'match_time': form.get('match_time', ''),
            'match_championship': form.get('match_championship', ''),
            'match_hidden': form.get('match_hidden') == 'on',
        }
    
    return segment_data, match_details, summary_text


def _validate_segment_base_data(segment_data):
    """Performs basic validation on common segment data fields."""
    errors = []
    if segment_data['position'] is None:
        errors.append("Position is required and must be an integer.")
    if not segment_data['type']:
        errors.append("Type is required.")
    if segment_data['type'] not in SEGMENT_TYPE_OPTIONS:
        errors.append(f"Invalid segment type: {segment_data['type']}.")
    return errors


@segments_bp.route('/create', methods=['GET', 'POST'])
def create_segment(event_slug):
    """Handles segment creation for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = _slugify(event_slug)

    all_wrestlers = load_active_wrestlers()
    all_tagteams = load_active_tagteams()

    summary_content = ""
    # Default match data for template if type is 'Match'
    match_data_for_template = {
        'sides': [],
        'participants_display': '',
        'match_result': '',
        'match_time': '',
        'match_championship': '',
        'match_hidden': False,
    }

    if request.method == 'POST':
        segment_data, match_details, summary_content = _get_segment_form_data(request.form)

        errors = _validate_segment_base_data(segment_data)
        
        if segment_data['type'] == 'Match':
            if match_details: # Ensure match_details is not None
                match_errors, match_warnings = validate_match_data(match_details['sides'])
                errors.extend(match_errors)
                for warning in match_warnings:
                    flash(warning, 'warning')
            else:
                errors.append("Match data is missing for a segment of type 'Match'.")
            
            # Update match_data_for_template with posted data for re-rendering
            if match_details:
                match_data_for_template.update(match_details)


        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('segments/form.html', event_slug=event_slug, segment=segment_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS,
                                   summary_content=summary_content,
                                   all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                                   match_data=match_data_for_template)

        success, message = add_segment(sluggified_event_name, segment_data, summary_content, match_details)
        if success:
            flash(message, 'success')
            return redirect(url_for('events.view_event', event_name=event_slug))
        else:
            flash(message, 'danger')

    return render_template('segments/form.html', event_slug=event_slug, segment={},
                           segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=summary_content,
                           all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                           match_data=match_data_for_template)


@segments_bp.route('/edit/<int:position>', methods=['GET', 'POST'])
def edit_segment(event_slug, position):
    """Handles segment editing for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = _slugify(event_slug)

    segment = get_segment_by_position(sluggified_event_name, position)
    if not segment:
        flash(f"Segment at position {position} not found for event '{event_slug}'.", 'danger')
        return redirect(url_for('events.view_event', event_name=event_slug))

    all_wrestlers = load_active_wrestlers()
    all_tagteams = load_active_tagteams()

    summary_content = load_summary_content(segment.get('summary_file', ''))
    
    # Initialize match_data for template, merging existing data if available
    match_data_for_template = {
        'sides': segment.get('sides', []),
        'participants_display': segment.get('participants_display', ''),
        'match_result': '', # Default, will be overridden if full match data exists
        'match_time': '',
        'match_championship': '',
        'match_hidden': False,
    }

    # If it's a match segment, load full match details
    if segment.get('type') == 'Match' and segment.get('match_id'):
        full_match = get_match_by_id(sluggified_event_name, segment['match_id'])
        if full_match:
            match_data_for_template.update({
                'match_result': full_match.get('match_result', ''),
                'match_time': full_match.get('match_time', ''),
                'match_championship': full_match.get('match_championship', ''),
                'match_hidden': full_match.get('match_hidden', False),
                'sides': full_match.get('sides', []), # Ensure full sides structure is passed
                'participants_display': full_match.get('participants_display', ''),
            })

    if request.method == 'POST':
        updated_segment_data, updated_match_details, new_summary_content = _get_segment_form_data(request.form)
        # Preserve original match_id if it exists, as it's not in the form
        if segment.get('match_id'):
            updated_segment_data['match_id'] = segment['match_id']

        errors = _validate_segment_base_data(updated_segment_data)

        if updated_segment_data['type'] == 'Match':
            if updated_match_details:
                match_errors, match_warnings = validate_match_data(updated_match_details['sides'])
                errors.extend(match_errors)
                for warning in match_warnings:
                    flash(warning, 'warning')
            else:
                errors.append("Match data is missing for a segment of type 'Match'.")
            
            # Update match_data_for_template with posted data for re-rendering
            if updated_match_details:
                match_data_for_template.update(updated_match_details)
        
        # If segment type changed from 'Match' to something else, clear match_data_for_template
        if segment.get('type') == 'Match' and updated_segment_data['type'] != 'Match':
             match_data_for_template = {
                'sides': [], 'participants_display': '', 'match_result': '',
                'match_time': '', 'match_championship': '', 'match_hidden': False,
            }


        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('segments/form.html', event_slug=event_slug, segment=updated_segment_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS,
                                   summary_content=new_summary_content, original_position=position,
                                   all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                                   match_data=match_data_for_template)

        success, message = update_segment(sluggified_event_name, position, updated_segment_data, new_summary_content, updated_match_details)
        if success:
            flash(message, 'success')
            return redirect(url_for('events.view_event', event_name=event_slug))
        else:
            flash(message, 'danger')
            # Re-render with updated_data if update failed due to conflict or other reason
            return render_template('segments/form.html', event_slug=event_slug, segment=updated_segment_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS,
                                   summary_content=new_summary_content, original_position=position,
                                   all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                                   match_data=match_data_for_template)

    return render_template('segments/form.html', event_slug=event_slug, segment=segment,
                           segment_type_options=SEGMENT_TYPE_OPTIONS,
                           summary_content=summary_content, original_position=position,
                           all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                           match_data=match_data_for_template)


@segments_bp.route('/delete/<int:position>', methods=['POST'])
def delete_segment_route(event_slug, position):
    """Handles segment deletion for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = _slugify(event_slug)

    success = delete_segment(sluggified_event_name, position)
    if success:
        flash(f"Segment at position {position} deleted successfully!", 'success')
    else:
        flash(f"Failed to delete segment at position {position}. Segment not found.", 'danger')
    return redirect(url_for('events.view_event', event_name=event_slug))
