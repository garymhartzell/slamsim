import os

import json

from functions import slugify_name, read_template, read_preferences, process_template

def create_events_future_page(events_data, prefs_data, output_file, header, footer):
    future_events = [event for event in events_data if event["Status"] == "Future"]
    future_events = sorted(future_events, key=lambda x: x["Date"])

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Future Events</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h1>Future Events</h1>
            <ul>
    """
    for event in future_events:
        event_slug = slugify_name(event["Name"])
        if event['Subtitle']:
            event_name = event['Name'] + ": " + event['Subtitle']
        else:
            event_name = event['Name']

        content += f'<li>{event["Date"]} <a href="events/{event_slug}.html">{event_name}</a> - {event["Location"]}</li>'

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
    print(f"Created future events page: {output_file}")

def create_events_year_pages(events_data, prefs_data, output_dir, header, footer):
    events_by_year = {}
    for event in events_data:
        if event["Status"] == "Past":
            year = event["Date"][:4]
            if year not in events_by_year:
                events_by_year[year] = []
            events_by_year[year].append(event)

    for year, events in events_by_year.items():
        events = sorted(events, key=lambda x: x["Date"])

        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Events of {year}</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h1>Events of {year}</h1>
            <ul>
        """
        for event in events:
            event_slug = slugify_name(event["Name"])
            if event['Subtitle']:
                event_name = event['Name'] + ": " + event['Subtitle']
            else:
                event_name = event['Name']

            content += f'<li>{event["Date"]} <a href="events/{event_slug}.html">{event_name}</a> - {event["Location"]}</li>'

        content += f"""
            </ul>
        </section>
    </main>

    {footer}
</body>
</html>
"""

        output_file = os.path.join(output_dir, f"events_{year}.html")
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as html_file:
            html_file.write(content)
        print(f"Created events page for year {year}: {output_file}")

def create_events_page(events_data, prefs_data, output_file, header, footer):
    years = sorted({event["Date"][:4] for event in events_data})

    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Events</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h1>Events</h1>
            <ul>
                <li><a href="events_future.html">Future Events</a></li>
    """
    for year in years:
        content += f'<li><a href="events_{year}.html">Events of {year}</a></li>'

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
    print(f"Created events index page: {output_file}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    events_json_file = os.path.join(base_dir, 'data/events.json')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')  # Path to prefs.json
    output_dir = os.path.join(base_dir, 'public')

    # Read preferences
    prefs_data = read_preferences(prefs_json_path)

    # Read and process templates
    header_template = read_template(os.path.join(base_dir, 'includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)

    # Read the JSON data
    with open(events_json_file, "r", encoding="utf-8") as f:
        events_data = json.load(f)

    # Create event pages
    create_events_future_page(events_data, prefs_data, os.path.join(output_dir, 'events_future.html'), header, footer)
    create_events_year_pages(events_data, prefs_data, output_dir, header, footer)
    create_events_page(events_data, prefs_data, os.path.join(output_dir, 'events.html'), header, footer)

if __name__ == "__main__":
    main()
    