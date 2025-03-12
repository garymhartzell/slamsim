import pandas as pd
from slugify import slugify 
from datetime import time
import json

def slugify_name(name):
    return slugify(name)

def read_template(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def escape_special_characters(value):
    if isinstance(value, str):
        return value.replace('"', r'&quot;')
    return value


def handle_dates_and_times(value):
    if pd.isnull(value):  # Check for NaT or NaN
        return ""
    elif isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")  # Format the date and time
    elif isinstance(value, time):
        return value.strftime("%M:%S")  # Format the time
    return value
def format_list(field):
    if isinstance(field, str):  # Ensure the field is a string
        items = field.split('|') if field else []
        formatted_items = "\n".join([f"<li>{item.strip()}</li>" for item in items])
        return formatted_items
    return ""  # Return an empty string if the field is not a string

def read_preferences(prefs_file):
    with open(prefs_file, "r", encoding="utf-8") as f:
        prefs_data = json.load(f)
    return {item["Pref"]: item["Value"] for item in prefs_data}

def process_template(template, prefs_data):
    for key, value in prefs_data.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template
    