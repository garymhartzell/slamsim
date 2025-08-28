import os
import json
from functions import slugify_name, read_template, format_list, handle_dates_and_times, read_preferences, process_template

def convert_to_int(value):
    try:
        return int(value)
    except ValueError:
        return 0

def create_html_files(data, prefs_data, output_dir, header, footer):
    os.makedirs(output_dir, exist_ok=True)
    
    for entry in data:
        name_slug = slugify_name(entry["Name"])
        file_path = os.path.join(output_dir, f"{name_slug}.html")

        # Convert relevant fields to integers
        singles_wins = convert_to_int(entry.get('Singles_Wins', 0))
        singles_losses = convert_to_int(entry.get('Singles_Losses', 0))
        singles_draws = convert_to_int(entry.get('Singles_Draws', 0))
        tag_wins = convert_to_int(entry.get('Tag_Wins', 0))
        tag_losses = convert_to_int(entry.get('Tag_Losses', 0))
        tag_draws = convert_to_int(entry.get('Tag_Draws', 0))

        total_wins = singles_wins + tag_wins
        total_losses = singles_losses + tag_losses
        total_draws = singles_draws + tag_draws

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
            <p><h2>{entry['Name']}</h2>
            {f"<p><h4>{entry.get('Belt', '')}</h4>" if entry.get('Belt') else ''}

            <p><h3>Vitals</h3>
            <ul>
                {f"<li><strong>Nickname:</strong> {entry.get('Nickname', '')}</li>" if entry.get('Nickname') else ''}
                {f"<li><strong>Location:</strong> {entry.get('Location', '')}</li>" if entry.get('Location') else ''}
                {f"<li><strong>Height:</strong> {entry.get('Height', '')}</li>" if entry.get('Height') else ''}
                {f"<li><strong>Weight:</strong> {entry.get('Weight', '')}</li>" if entry.get('Weight') else ''}
                {f"<li><strong>Date of Birth:</strong> {entry.get('DOB', '')}</li>" if entry.get('DOB') else ''}
                {f"<li><strong>Alignment:</strong> {entry.get('Alignment', '')}</li>" if entry.get('Alignment') else ''}
                {f"<li><strong>Music:</strong> {entry.get('Music', '')}</li>" if entry.get('Music') else ''}
                {f"<li><strong>Manager:</strong> {entry.get('Manager', '')}</li>" if entry.get('Manager') else ''}
                {f"<li><strong>Tag-Team:</strong> {entry.get('Team', '')}</li>" if entry.get('Team') else ''}
                {f"<li><strong>Faction:</strong> {entry.get('Faction')}</li>" if entry.get('Faction') else ''}
            </ul>

            {f"<p><h3>Moves</h3><ul>{format_list(entry.get('Moves', ''))}</ul>" if entry.get('Moves') else ''}

            <p><h3>Records</h3>
            <ul>
                {f"<li><strong>Singles:</strong> {singles_wins}-{singles_losses}-{singles_draws}</li>"}
                {f"<li><strong>Tag-Team:</strong> {tag_wins}-{tag_losses}-{tag_draws}</li>"}
                {f"<li><strong>Overall:</strong> {total_wins}-{total_losses}-{total_draws}</li>"}
            </ul>

            {f"<p><h3>Accomplishments</h3><ul>{format_list(entry.get('Awards', ''))}</ul>" if entry.get('Awards') else ''}

            <p><h3>Personal Info</h3>
            <ul>
            <li><strong>Real Name:</strong> {entry.get('Real_Name', '')}</li>
            <li><strong>Start Date:</strong> {entry.get('Start_Date', '')}</li>
            </ul>

            {f"<p><h3>Salary History</h3><ul>{format_list(entry.get('Salary', ''))}</ul>" if entry.get('Salary') else ''}

        </section>
    </main>

    {footer}
</body>
</html>
"""

        with open(file_path, "w", encoding="utf-8") as html_file:
            html_file.write(content)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_file = os.path.join(base_dir, 'data/wrestlers.json')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')
    output_dir_html = os.path.join(base_dir, 'public/wrestlers')

    # Read preferences
    prefs_data = read_preferences(prefs_json_path)

    header_template = read_template(os.path.join(base_dir, 'includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))

    # Process templates with preferences
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)

    # Read the JSON data
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create HTML files
    create_html_files(data, prefs_data, output_dir_html, header, footer)

    print(f"HTML files for wrestlers created successfully!")

if __name__ == "__main__":
    main()
