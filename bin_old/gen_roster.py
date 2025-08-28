import json
import os
from functions import slugify_name, read_template, read_preferences, process_template

def create_roster_page(wrestlers_data, tagteams_data, divisions_data, prefs_data, output_dir, header, footer):
    file_path = os.path.join(output_dir, "roster.html")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Initialize divisions dictionary based on divisions.json
    divisions = {division["Name"]: [] for division in divisions_data if division["Status"] == "Active"}
    division_id_to_name = {division["ID"]: division["Name"] for division in divisions_data if division["Status"] == "Active"}

    # Filter and sort wrestlers for each division
    for entry in wrestlers_data:
        if entry["Status"] == "Active":
            division_id = entry.get("Division")
            # Handle both integer and float division IDs
            division_name = division_id_to_name.get(int(division_id), division_id_to_name.get(division_id))
            if division_name in divisions:
                divisions[division_name].append(entry)

    # Filter and sort tag-teams for each division
    for entry in tagteams_data:
        if entry["Status"] == "Active":
            division_id = entry.get("Division")
            # Handle both integer and float division IDs
            division_name = division_id_to_name.get(int(division_id), division_id_to_name.get(division_id))
            if division_name in divisions:
                divisions[division_name].append(entry)

    # Sort each division by name
    for division in divisions:
        divisions[division] = sorted(divisions[division], key=lambda x: x.get("Name", ""))

    # Create HTML content for roster
    content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roster</title>
</head>
<body>
    {header}

    <main>
        <section>
            <h2>Roster</h2>
    """

    for division, participants in divisions.items():
        content += f"<h3>{division}</h3><ul>"
        if participants:
            for participant in participants:
                name = participant["Name"]
                status_or_belt = ""
                if participant.get("Status") in ["Injured", "Leave", "Suspended"]:
                    status_or_belt = f"({participant.get('Status')})"
                elif participant.get("Belt"):
                    status_or_belt = f"({participant.get('Belt')})"

                content += f'<li><a href="{"wrestlers" if "Singles" in division else "tagteams"}/{slugify_name(name)}.html">{name}</a> {status_or_belt}</li>'
            content += "</ul>"
        else:
            content += "<li>No participants</li>"

    content += f"""
        </section>
    </main>

    {footer}
</body>
</html>
"""

    # Write to HTML file
    with open(file_path, "w", encoding="utf-8") as html_file:
        html_file.write(content)
        print(f"Written HTML content to {file_path}")

def main():
    # Paths to JSON files, templates, and output directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wrestlers_json_path = os.path.join(base_dir, 'data/wrestlers.json')
    tagteams_json_path = os.path.join(base_dir, 'data/tagteams.json')
    divisions_json_path = os.path.join(base_dir, 'data/divisions.json')
    prefs_json_path = os.path.join(base_dir, 'data/prefs.json')
    output_dir_html = os.path.join(base_dir, 'public')

# Read the templates
    header_template = read_template(os.path.join(base_dir, 'includes/header.html'))
    footer_template = read_template(os.path.join(base_dir, 'includes/footer.html'))

    # Read the preferences
    prefs_data = read_preferences(prefs_json_path)

    # Process templates with preferences
    header = process_template(header_template, prefs_data)
    footer = process_template(footer_template, prefs_data)
    
    # Read the JSON data
    
    with open(wrestlers_json_path, "r", encoding="utf-8") as f:
        wrestlers_data = json.load(f)
    with open(tagteams_json_path, "r", encoding="utf-8") as f:
        tagteams_data = json.load(f)
    with open(divisions_json_path, "r", encoding="utf-8") as f:
        divisions_data = json.load(f)

    # Generate roster page
    create_roster_page(wrestlers_data, tagteams_data, divisions_data, prefs_data, output_dir_html, header, footer)

    print("Roster page created successfully!")

if __name__ == "__main__":
    main()
