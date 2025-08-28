import os
import json
from functions import slugify_name, read_template, read_preferences, process_template

def create_event_page(event, matches_data, prefs_data, output_dir, header, footer):
    event_name_slug = slugify_name(event["Name"])
    file_path = os.path.join(output_dir, f"{event_name_slug}.html")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    summary_file = event.get('Summary_File', '').strip()
    event_summary = ""
    if summary_file:
        summary_file_path = os.path.join('includes', 'events', summary_file)
        try:
            event_summary = read_template(summary_file_path)
        except FileNotFoundError:
            print(f"Warning: Summary file '{summary_file_path}' not found. Continuing without event summary.")
    else:
        print(f"Warning: No summary file provided for event '{event['Name']}'. Continuing without event summary.")

    # Build Event Name
    if event.get('Subtitle'):
        event_name = event['Name'] + ": " + event['Subtitle']
    else:
        event_name = event['Name']

    # Extract event matches and sort
    event_matches = [match for match in matches_data if match["Event"] == event["Name"]]
    event_matches = sorted(event_matches, key=lambda x: x.get("Number", 0))

    # Generate HTML content for the event page
    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{event['Name']}</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h2>{event_name}</h2>
            <p><strong>Date:</strong> {event.get('Date', '')}</p>
            <p><strong>Venue:</strong> {event['Venue']} in {event['Location']}</p>
            <p><strong>Broadcasters:</strong> {event['Broadcasters']}</p>

            <h3>Event Card</h3>
            <ul>
    """
    for match in event_matches:
        if match.get('Hidden') in (None, ''):
            header_match = match.get('Header', '')
            participants = match.get('Participants', '')
            if header_match:
                content += f"<li>{header_match}: {participants}</li>"
            else:
                content += f"<li>{participants}</li>"

    content += "</ul>"
    content += f"""
            <h3>Summary</h3>
            <div>{event_summary or 'No summary available for this event.'}</div>

            <h3>Results</h3>
            <ul>
    """
    for match in event_matches:
        result = match.get('Result', 'No result available')
        time = match.get('Time', 'N/A')
        content += f"<li>{result} ({time})</li>"

    content += "</ul>"

    content += f"""
        </section>
    </main>

    {footer}
</body>
</html>
"""

    with open(file_path, "w", encoding="utf-8") as html_file:
        html_file.write(content)

    print(f"Created event page: {file_path}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_json_file = os.path.join(base_dir, 'data/events.json')
    matches_json_file = os.path.join(base_dir, 'data/matches.json')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')
    output_dir_events = os.path.join(base_dir, 'public/events')

    prefs_data = read_preferences(prefs_json_path)
    header_template = read_template(os.path.join(base_dir, 'includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))

    # Process templates with preferences
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)

    # Read the JSON data
    with open(events_json_file, "r", encoding="utf-8") as f:
        events_data = json.load(f)
    with open(matches_json_file, "r", encoding="utf-8") as f:
        matches_data = json.load(f)

    # Create event pages
    for event in events_data:
        create_event_page(event, matches_data, prefs_data, output_dir_events, header, footer)

    print("Event pages created successfully!")

if __name__ == "__main__":
    main()