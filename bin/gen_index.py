import os
import json

from functions import slugify_name, read_template, read_preferences, process_template

def create_index_page(news_data, events_data, wrestlers_data, tagteams_data, prefs_data, output_file, header, footer):
    news_data_sorted = sorted(news_data, key=lambda x: x['Date'], reverse=True)
    latest_articles = news_data_sorted[:5]

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h2>Latest News</h2>
            <ul>
    """
    for article in latest_articles:
        link = os.path.join('news', article['Content_File'])
        content += f'<li>{article["Date"]}&nbsp<a href="{link}">{article["Title"]}</a></li>'

    content += f"""
            </ul>
            <h2>Recent Events</h2>
            <ul>
    """
    for event in events_data:
        if event["Status"] == "Past":
            event_slug = slugify_name(event["Name"])
            if event['Subtitle']:
                event_name = event['Name'] + ": " + event['Subtitle']
            else:
                event_name = event['Name']
            content += f'<li>{event["Date"]} <a href="events/{event_slug}.html">{event_name}</a> - {event["Location"]}</li>'

    content += """
            </ul>

            <h2>Upcoming Events</h2>
            <ul>
    """
    for event in events_data:
        if event["Status"] == "Future":
            event_slug = slugify_name(event["Name"])
            if event['Subtitle']:
                event_name = event['Name'] + ": " + event['Subtitle']
            else:
                event_name = event['Name']
            content += f'<li>{event["Date"]} <a href="events/{event_slug}.html">{event_name}</a> - {event["Location"]}</li>'

    content += """
            </ul>

            <h2>Current Champions</h2>
            <ul>
    """
    for champion in wrestlers_data + tagteams_data:
        if champion["Belt"]:
            name_slug = slugify_name(champion["Name"])
            content += f'<li><a href="wrestlers/{name_slug}.html">{champion["Name"]} - {champion["Belt"]}</a></li>'

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
    print(f"Created index page: {output_file}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_json_file = os.path.join(base_dir, 'data/events.json')
    news_json_file = os.path.join(base_dir, 'data/news.json')
    wrestlers_json_file = os.path.join(base_dir, 'data/wrestlers.json')
    tagteams_json_file = os.path.join(base_dir, 'data/tagteams.json')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')
    output_file = os.path.join(base_dir, 'public/index.html')

    prefs_data = read_preferences(prefs_json_path)
    header_template = read_template(os.path.join(base_dir, 'includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))

    # Process templates with preferences
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)

    # Read the JSON data
    with open(news_json_file, "r", encoding="utf-8") as f:
        news_data = json.load(f)

    with open(events_json_file, "r", encoding="utf-8") as f:
        events_data = json.load(f)
    with open(wrestlers_json_file, "r", encoding="utf-8") as f:
        wrestlers_data = json.load(f)
    with open(tagteams_json_file, "r", encoding="utf-8") as f:
        tagteams_data = json.load(f)

    # Create index page
    create_index_page(news_data, events_data, wrestlers_data, tagteams_data, prefs_data, output_file, header, footer)

if __name__ == "__main__":
    main()
    