import json
import os

from functions import slugify_name, read_template, read_preferences, process_template, escape_special_characters, format_list

def create_html_files(data, output_dir, header, footer):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for entry in data:
        name_slug = slugify_name(entry["Name"])
        file_path = os.path.join(output_dir, f"{name_slug}.html")

        # Create HTML content
        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{entry['Name']}</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h2>{entry['Name']}</h2>
            {f"<p><h4>{entry.get('Belt', '')}</h4>" if entry.get('Belt') else ''}

            {f"<p><h3>Team Members</h3><ul>{format_list(entry.get('Members', ''))}</ul>" if entry.get('Members') else ''}    
            
            <p><h3>Vitals</h3>
            <ul>
                {f"<li><strong>Location:</strong> {entry.get('Location', '')}</li>" if entry.get('Location') else ''}
                {f"<li><strong>Combined Weight:</strong> {entry.get('Weight', '')}</li>" if entry.get('Weight') else ''}
                {f"<li><strong>Record:</strong> { entry.get('Wins') }-{ entry.get('Losses') }-{ entry.get('Draws') }</li>"}
                {f"<li><strong>Alignment:</strong> {entry.get('Alignment', '')}</li>" if entry.get('Alignment') else ''}
                {f"<li><strong>Music:</strong> {entry.get('Music', '')}</li>" if entry.get('Music') else ''}
                {f"<li><strong>Faction:</strong> {entry.get('Faction', '')}</li>" if entry.get('Faction') else ''}
                {f"<li><strong>Manager:</strong> {entry.get('Manager', '')}</li>" if entry.get('Manager') else ''}
            </ul>

            {f"<p><h3>Moves</h3><ul>{format_list(entry.get('Moves', ''))}</ul>" if entry.get('Moves') else ''}
            {f"<p><h3>Accomplishments</h3><ul>{format_list(entry.get('Awards', ''))}</ul>" if entry.get('Awards') else ''}

        </section>
    </main>

    {footer}
</body>
</html>
"""

        # Write to HTML file
        with open(file_path, "w", encoding="utf-8") as html_file:
            html_file.write(content)

def main():

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file = os.path.join(base_dir, 'data/tagteams.json')
    output_dir_html = os.path.join(base_dir, 'public/tagteams')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')  # Path to prefs.json

    # Read the templates
    header_template = read_template(os.path.join('includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))

    # Read the JSON data
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Read preferences
    prefs_data = read_preferences(prefs_json_path)

    # Process templates with preferences
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)

    # Create HTML files
    create_html_files(data, output_dir_html, header, footer)

    print("HTML files for tagteams created successfully!")

if __name__ == "__main__":
    main()
    