import os
import json

from functions import read_template, read_preferences, process_template

def create_individual_news_page(article, prefs_data, header, footer):
    content_file = os.path.join('includes/news', article['Content_File'])
    with open(content_file, 'r', encoding='utf-8') as f:
        article_content = f.read()

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['Title']}</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h2>{article['Title']}</h2>
            <p><strong>Posted:</strong> {article['Date']}</p>
            <div>
                {article_content}
            </div>
        </section>
    </main>

    {footer}
</body>
</html>
"""

    # Ensure the output directory exists
    output_file = os.path.join('public/news', article['Content_File'])
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as html_file:
        html_file.write(content)
    print(f"Created individual news page: {output_file}")

def create_news_listing_page(news_data, prefs_data, output_file, header, footer):
    news_data_sorted = sorted(news_data, key=lambda x: x['Date'], reverse=True)
    latest_articles = news_data_sorted[:5]
    years = sorted({article['Date'][:4] for article in news_data_sorted})

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h3>Latest News</h3>
            <ul>
    """
    for article in latest_articles:
        link = os.path.join('news', article['Content_File'])
        content += f'<li>{article["Date"]}&nbsp<a href="{link}">{article["Title"]}</a></li>'

    content += f"""
            </ul>
        </section>
        <section>
            <h3>News Archives</h3>
            <ul>
    """
    for year in years:
        content += f'<li><a href="news_{year}.html">News from {year}</a></li>'

    content += f"""
            </ul>
        </section>
    </main>

    {footer}
</body>
</html>
"""

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as html_file:
        html_file.write(content)
    print(f"Created news listing page: {output_file}")

def create_news_year_page(news_data, year, prefs_data, output_file, header, footer):
    news_data_sorted = sorted([article for article in news_data if article['Date'].startswith(year)], key=lambda x: x['Date'], reverse=True)

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News from {year}</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h2>News from {year}</h2>
            <ul>
    """
    for article in news_data_sorted:
        link = os.path.join('news', article['Content_File'])
        content += f'<li><a href="{link}">{article["Title"]} - {article["Date"]}</a></li>'

    content += f"""
            </ul>
        </section>
    </main>

    {footer}
</body>
</html>
"""

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as html_file:
        html_file.write(content)
    print(f"Created news year page: {output_file}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    news_json_file = os.path.join(base_dir, 'data/news.json')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')
    output_file_news = os.path.join(base_dir, 'public/news.html')

    # Read the JSON data FIRST
    with open(news_json_file, "r", encoding="utf-8") as f:
        news_data = json.load(f)

    # Read the templates
    header_template = read_template(os.path.join(base_dir, 'includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))

    # Read the preferences
    prefs_data = read_preferences(prefs_json_path)

    # Process templates with preferences
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)

    # Create individual news pages
    for article in news_data:
        create_individual_news_page(article, prefs_data, header, footer)

    # Create news listing pages
    create_news_listing_page(news_data, prefs_data, output_file_news, header, footer) #<--- header, not header_template
    years = sorted({article['Date'][:4] for article in news_data})
    for year in years:
        output_file_year = os.path.join(base_dir, f'public/news_{year}.html')
        create_news_year_page(news_data, year, prefs_data, output_file_year, header, footer) #<--- header, not header_template

if __name__ == "__main__":
    main()
    