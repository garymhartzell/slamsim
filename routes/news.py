from flask import Blueprint, render_template, request, url_for, flash, redirect
from src.news import (
    load_news_posts, get_news_post_by_id, add_news_post,
    update_news_post, delete_news_post, NEWS_DATE_FORMAT
)
from src.prefs import load_preferences, save_preferences # Import save_preferences
from src.date_utils import get_current_working_date # Import the new utility
from datetime import datetime
import markdown

news_bp = Blueprint('news', __name__, url_prefix='/news')

def _get_form_data(form, is_create=False):
    """Extracts and validates form data for a news post."""
    data = {
        'Date': form.get('date'),
        'Subject': form.get('subject'),
        'Content': form.get('content', '')
    }

    errors = {}
    if not data['Date']:
        errors['date'] = 'Date is required.'
    else:
        try:
            datetime.strptime(data['Date'], NEWS_DATE_FORMAT)
        except ValueError:
            errors['date'] = f'Date must be in {NEWS_DATE_FORMAT} format.'
    
    if not data['Subject']:
        errors['subject'] = 'Subject is required.'

    return data, errors

@news_bp.route('/')
def list_news():
    """Renders the list of all news posts."""
    news_posts = load_news_posts()
    return render_template('booker/news/list.html', news_posts=news_posts)

@news_bp.route('/create', methods=['GET', 'POST'])
def create_news():
    """Handles the creation of a new news post."""
    prefs = load_preferences() # Load preferences here
    current_working_date = get_current_working_date().strftime(NEWS_DATE_FORMAT) # Get the current working date

    if request.method == 'POST':
        news_data, errors = _get_form_data(request.form, is_create=True)
        if errors:
            for field, msg in errors.items():
                flash(msg, 'danger')
            # Pass back form data for re-population
            news_post_for_form = {'Date': news_data.get('Date', current_working_date), # Use current_working_date as fallback
                                  'Subject': news_data.get('Subject', ''),
                                  'Content': news_data.get('Content', '')}
            return render_template('booker/news/form.html', news_post=news_post_for_form, form_action='create', prefs=prefs)
        
        add_news_post(news_data)

        # Update game_date if checkbox is checked and mode is 'latest-event-date'
        if prefs.get('game_date_mode') == 'latest-event-date' and request.form.get('update_game_date'):
            prefs['game_date'] = news_data['Date']
            save_preferences(prefs)
            flash(f"Game date updated to {news_data['Date']}.", 'info')

        flash('News post created successfully!', 'success')
        return redirect(url_for('news.list_news'))
    
    # Pre-fill date for GET request with current working date
    return render_template('booker/news/form.html', news_post={'Date': current_working_date}, form_action='create', prefs=prefs)

@news_bp.route('/edit/<string:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    """Handles the editing of an existing news post."""
    prefs = load_preferences() # Load preferences here
    current_working_date = get_current_working_date().strftime(NEWS_DATE_FORMAT) # Get the current working date

    news_post = get_news_post_by_id(news_id)
    if not news_post:
        flash('News post not found.', 'danger')
        return redirect(url_for('news.list_news'))

    if request.method == 'POST':
        news_data, errors = _get_form_data(request.form)
        if errors:
            for field, msg in errors.items():
                flash(msg, 'danger')
            news_data['News_ID'] = news_id # Ensure ID is present for template
            # Pass back form data for re-population
            news_post_for_form = {'News_ID': news_id,
                                  'Date': news_data.get('Date', news_post.get('Date')),
                                  'Subject': news_data.get('Subject', news_post.get('Subject')),
                                  'Content': news_data.get('Content', news_post.get('Content'))}
            return render_template('booker/news/form.html', news_post=news_post_for_form, form_action='edit', prefs=prefs)
        
        update_news_post(news_id, news_data)

        # Update game_date if checkbox is checked and mode is 'latest-event-date'
        if prefs.get('game_date_mode') == 'latest-event-date' and request.form.get('update_game_date'):
            prefs['game_date'] = news_data['Date']
            save_preferences(prefs)
            flash(f"Game date updated to {news_data['Date']}.", 'info')

        flash('News post updated successfully!', 'success')
        return redirect(url_for('news.list_news'))

    return render_template('booker/news/form.html', news_post=news_post, form_action='edit', prefs=prefs)

@news_bp.route('/view/<string:news_id>')
def view_news(news_id):
    """Renders a single news post."""
    news_post = get_news_post_by_id(news_id)
    if not news_post:
        flash('News post not found.', 'danger')
        return redirect(url_for('news.list_news'))
    
    # Render markdown content to HTML
    news_post['RenderedContent'] = markdown.markdown(news_post.get('Content', ''))
    
    return render_template('booker/news/view.html', news_post=news_post)

@news_bp.route('/delete/<string:news_id>', methods=['POST'])
def delete_news_route(news_id):
    """Handles the deletion of a news post."""
    if delete_news_post(news_id):
        flash('News post deleted successfully!', 'success')
    else:
        flash('News post not found.', 'danger')
    return redirect(url_for('news.list_news'))
