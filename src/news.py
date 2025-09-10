import json
import os
import uuid
from datetime import datetime

NEWS_FILE_RELATIVE_TO_ROOT = 'data/news.json'
NEWS_DATE_FORMAT = '%Y-%m-%d'

def _get_news_file_path():
    """Constructs the absolute path to the news data file."""
    # This assumes the script is run from the project root or src directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, NEWS_FILE_RELATIVE_TO_ROOT)

def load_news_posts():
    """Loads all news posts from the JSON file."""
    file_path = _get_news_file_path()
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        news_posts = json.load(f)
    
    # Ensure all posts have a News_ID and sort by date descending
    for post in news_posts:
        if 'News_ID' not in post:
            post['News_ID'] = str(uuid.uuid4())
        # Ensure Content field exists for consistency
        if 'Content' not in post and 'Content_File' in post:
            # For backward compatibility with old content files
            # This logic can be removed after migration
            try:
                # Assuming content files are in 'includes/news/'
                content_file_path = os.path.join(os.path.dirname(file_path), '../includes/news/', post['Content_File'])
                with open(content_file_path, 'r', encoding='utf-8') as cf:
                    post['Content'] = cf.read()
            except FileNotFoundError:
                post['Content'] = '' # Default if file not found
            del post['Content_File'] # Remove old field

        if 'Content' not in post: # Ensure it exists after potential migration
            post['Content'] = ''

        # Rename 'Title' to 'Subject' if 'Title' exists and 'Subject' doesn't
        if 'Title' in post and 'Subject' not in post:
            post['Subject'] = post['Title']
            del post['Title']
        elif 'Subject' not in post: # Ensure Subject exists
            post['Subject'] = ''

    # Sort posts by date, newest first
    try:
        news_posts.sort(key=lambda x: datetime.strptime(x.get('Date', '1970-01-01'), NEWS_DATE_FORMAT), reverse=True)
    except ValueError:
        # Fallback if date format is inconsistent
        pass

    return news_posts

def save_news_posts(news_posts_list):
    """Saves the list of news posts to the JSON file."""
    file_path = _get_news_file_path()
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(news_posts_list, f, indent=4)

def get_news_post_by_id(news_id):
    """Retrieves a single news post by its ID."""
    news_posts = load_news_posts()
    return next((post for post in news_posts if post.get('News_ID') == news_id), None)

def add_news_post(news_data):
    """Adds a new news post to the list."""
    news_posts = load_news_posts()
    news_data['News_ID'] = str(uuid.uuid4())
    news_posts.append(news_data)
    save_news_posts(news_posts)
    return news_data['News_ID']

def update_news_post(news_id, updated_data):
    """Updates an existing news post."""
    news_posts = load_news_posts()
    for i, post in enumerate(news_posts):
        if post.get('News_ID') == news_id:
            news_posts[i].update(updated_data)
            save_news_posts(news_posts)
            return True
    return False

def delete_news_post(news_id):
    """Deletes a news post by its ID."""
    news_posts = load_news_posts()
    original_count = len(news_posts)
    news_posts = [post for post in news_posts if post.get('News_ID') != news_id]
    if len(news_posts) < original_count:
        save_news_posts(news_posts)
        return True
    return False
