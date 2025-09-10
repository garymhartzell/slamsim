from flask import Blueprint, render_template, request, url_for, flash, redirect
from src.news import (
    load_news_posts, get_news_post_by_id, add_news_post,
    update_news_post, delete_news_post, NEWS_DATE_FORMAT
)
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
    return render_template('news/list.html', news_posts=news_posts)

@news_bp.route('/create', methods=['GET', 'POST'])
def create_news():
    """Handles the creation of a new news post."""
    if request.method == 'POST':
        news_data, errors = _get_form_data(request.form, is_create=True)
        if errors:
            for field, msg in errors.items():
                flash(msg, 'danger')
            # Pass back form data for re-population
            news_post_for_form = {'Date': news_data.get('Date', datetime.now().strftime(NEWS_DATE_FORMAT)),
                                  'Subject': news_data.get('Subject', ''),
                                  'Content': news_data.get('Content', '')}
            return render_template('news/form.html', news_post=news_post_for_form, form_action='create')
        
        add_news_post(news_data)
        flash('News post created successfully!', 'success')
        return redirect(url_for('news.list_news'))
    
    # Pre-fill date for GET request
    default_date = datetime.now().strftime(NEWS_DATE_FORMAT)
    return render_template('news/form.html', news_post={'Date': default_date}, form_action='create')

@news_bp.route('/edit/<string:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    """Handles the editing of an existing news post."""
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
            return render_template('news/form.html', news_post=news_post_for_form, form_action='edit')
        
        update_news_post(news_id, news_data)
        flash('News post updated successfully!', 'success')
        return redirect(url_for('news.list_news'))

    return render_template('news/form.html', news_post=news_post, form_action='edit')

@news_bp.route('/view/<string:news_id>')
def view_news(news_id):
    """Renders a single news post."""
    news_post = get_news_post_by_id(news_id)
    if not news_post:
        flash('News post not found.', 'danger')
        return redirect(url_for('news.list_news'))
    
    # Render markdown content to HTML
    news_post['RenderedContent'] = markdown.markdown(news_post.get('Content', ''))
    
    return render_template('news/view.html', news_post=news_post)

@news_bp.route('/delete/<string:news_id>', methods=['POST'])
def delete_news_route(news_id):
    """Handles the deletion of a news post."""
    if delete_news_post(news_id):
        flash('News post deleted successfully!', 'success')
    else:
        flash('News post not found.', 'danger')
    return redirect(url_for('news.list_news'))
