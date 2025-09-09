from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.segments import (
    load_segments, get_segment_by_position, add_segment, update_segment, delete_segment,
    load_summary_content, _slugify, delete_all_segments_for_event,
    load_active_wrestlers, load_active_tagteams, get_match_by_id,
    generate_match_display_string, validate_match_data
)
from src.events import get_event_by_name
from src.belts import load_belts
import json

segments_bp = Blueprint('segments', __name__, url_prefix='/events/<string:event_slug>/segments')

SEGMENT_TYPE_OPTIONS = ["Match", "Promo", "Interview", "In-ring", "Brawl"]
MATCH_RESULT_OPTIONS = ["Win", "Loss", "Draw", "No Contest"]

def _get_segment_form_data(form):
    """Extracts segment data from the form, including new match participant and result data."""
    position_str = form.get('position')
    position = int(position_str) if position_str and position_str.isdigit() else None
    
    segment_type = form.get('type')
    header = form.get('header', '')
    summary_text = form.get('summary_text', '')

    segment_data = {
        'position': position,
        'type': segment_type,
        'header': header,
    }

    match_details = None
    if segment_type == 'Match':
        match_sides_json = form.get('match_sides_json', '[]')
        match_sides = json.loads(match_sides_json)
        participants_display = form.get('participants_display', '')
        
        match_results_json = form.get('match_results_json', '{}')
        match_results_data = json.loads(match_results_json)

        match_details = {
            'participants_display': participants_display,
            'sides': match_sides,
            'match_time': form.get('match_time', ''),
            'match_championship': form.get('match_championship', ''),
            'match_hidden': form.get('match_hidden') == 'on',
            'match_class': form.get('match_class', ''),
            'winning_side_index': match_results_data.get('winning_side_index', -1),
            'individual_results': match_results_data.get('individual_results', {}),
            'team_results': match_results_data.get('team_results', {}),
            'sync_teams_to_individuals': match_results_data.get('sync_teams_to_individuals', True),
            'warnings': [],
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
    all_wrestlers = sorted(load_active_wrestlers(), key=lambda w: w['Name'])
    all_tagteams = sorted(load_active_tagteams(), key=lambda t: t['Name'])
    all_belts = load_belts()

    match_data_for_template = {
        'sides': [], 'participants_display': '', 'match_time': '',
        'match_championship': '', 'match_hidden': False,
        'match_class': '', 'winning_side_index': -1, 'individual_results': {},
        'team_results': {}, 'sync_teams_to_individuals': True, 'warnings': [],
    }

    if request.method == 'POST':
        segment_data, match_details, summary_content = _get_segment_form_data(request.form)
        errors = _validate_segment_base_data(segment_data)
        
        if segment_data['type'] == 'Match':
            if match_details:
                match_errors, match_warnings = validate_match_data(match_details['sides'], match_details)
                errors.extend(match_errors)
                match_details['warnings'] = match_warnings
                match_data_for_template.update(match_details)
            else:
                errors.append("Match data is missing for a segment of type 'Match'.")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('segments/form.html', event_slug=event_slug, segment=segment_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=summary_content,
                                   all_wrestlers=all_wrestlers, all_tagteams=all_tagteams, all_belts=all_belts,
                                   match_data=match_data_for_template, match_result_options=MATCH_RESULT_OPTIONS)

        try:
            success, message = add_segment(sluggified_event_name, segment_data, summary_content, match_details)
            if success:
                flash(message, 'success')
                return redirect(url_for('events.edit_event', event_name=event_slug))
            else:
                flash(message, 'danger')
        except ValueError as e:
            flash(str(e), 'danger')

        return render_template('segments/form.html', event_slug=event_slug, segment=segment_data,
                               segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=summary_content,
                               all_wrestlers=all_wrestlers, all_tagteams=all_tagteams, all_belts=all_belts,
                               match_data=match_data_for_template, match_result_options=MATCH_RESULT_OPTIONS)

    return render_template('segments/form.html', event_slug=event_slug, segment={},
                           segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content="",
                           all_wrestlers=all_wrestlers, all_tagteams=all_tagteams, all_belts=all_belts,
                           match_data=match_data_for_template, match_result_options=MATCH_RESULT_OPTIONS)

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
        flash(f"Segment at position {position} not found.", 'danger')
        return redirect(url_for('events.edit_event', event_name=event_slug))

    all_wrestlers = sorted(load_active_wrestlers(), key=lambda w: w['Name'])
    all_tagteams = sorted(load_active_tagteams(), key=lambda t: t['Name'])
    all_belts = load_belts()
    summary_content = load_summary_content(segment.get('summary_file', ''))
    
    match_data_for_template = {}
    if segment.get('type') == 'Match' and segment.get('match_id'):
        full_match = get_match_by_id(sluggified_event_name, segment['match_id'])
        if full_match:
            match_data_for_template = full_match

    if request.method == 'POST':
        updated_segment_data, updated_match_details, new_summary_content = _get_segment_form_data(request.form)
        errors = _validate_segment_base_data(updated_segment_data)

        if updated_segment_data['type'] == 'Match':
            if updated_match_details:
                match_errors, match_warnings = validate_match_data(updated_match_details['sides'], updated_match_details)
                errors.extend(match_errors)
                updated_match_details['warnings'] = match_warnings
            else:
                errors.append("Match data is missing for a segment of type 'Match'.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('segments/form.html', event_slug=event_slug, segment=updated_segment_data,
                                   segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=new_summary_content,
                                   original_position=position, all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                                   all_belts=all_belts, match_data=updated_match_details or {}, match_result_options=MATCH_RESULT_OPTIONS)
        try:
            success, message = update_segment(sluggified_event_name, position, updated_segment_data, new_summary_content, updated_match_details)
            if success:
                flash(message, 'success')
                return redirect(url_for('events.edit_event', event_name=event_slug))
            else:
                flash(message, 'danger')
        except ValueError as e:
            flash(str(e), 'danger')
        
        return render_template('segments/form.html', event_slug=event_slug, segment=updated_segment_data,
                               segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=new_summary_content,
                               original_position=position, all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                               all_belts=all_belts, match_data=updated_match_details or {}, match_result_options=MATCH_RESULT_OPTIONS)

    return render_template('segments/form.html', event_slug=event_slug, segment=segment,
                           segment_type_options=SEGMENT_TYPE_OPTIONS, summary_content=summary_content,
                           original_position=position, all_wrestlers=all_wrestlers, all_tagteams=all_tagteams,
                           all_belts=all_belts, match_data=match_data_for_template,
                           match_result_options=MATCH_RESULT_OPTIONS)

@segments_bp.route('/delete/<int:position>', methods=['POST'])
def delete_segment_route(event_slug, position):
    """Handles segment deletion for a specific event."""
    event = get_event_by_name(event_slug)
    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('events.list_events'))

    sluggified_event_name = _slugify(event_slug)
    if delete_segment(sluggified_event_name, position):
        flash(f"Segment at position {position} deleted successfully!", 'success')
    else:
        flash(f"Failed to delete segment at position {position}.", 'danger')
    return redirect(url_for('events.edit_event', event_name=event_slug))

