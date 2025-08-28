import csv
import json
import argparse
import os

def csv_to_json(csv_file_path, output_file_path):
    """Converts a CSV file to JSON and writes it to a file, removing BOM."""
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)

            if data and "\ufeff" in list(data[0].keys())[0]:
                first_row = data[0]
                first_key = list(first_row.keys())[0]
                new_first_key = first_key.replace("\ufeff", "")
                first_row[new_first_key] = first_row.pop(first_key)

            for row in data:
                for key, value in row.items():
                    row[key] = str(value)

        with open(output_file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4)

        return f"Successfully converted '{csv_file_path}' to '{output_file_path}'"

    except FileNotFoundError:
        return f"Error: File '{csv_file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"

def batch_convert(directory):
    """Converts all CSV files in a directory to JSON."""
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            csv_file_path = os.path.join(directory, filename)
            base_name = os.path.splitext(csv_file_path)[0]
            output_file_path = base_name + ".json"
            result = csv_to_json(csv_file_path, output_file_path)
            print(result)

def main():
    """Handles command-line arguments and batch processing."""
    parser = argparse.ArgumentParser(description="Convert CSV to JSON (single or batch).")
    parser.add_argument("-f", "--file", help="Path to the CSV file (single file mode).")
    parser.add_argument("-b", "--batch", help="Path to the directory containing CSV files (batch mode).")
    args = parser.parse_args()

    if args.batch:
        batch_convert(args.batch)
    elif args.file:
        csv_file_path = args.file
        base_name = os.path.splitext(csv_file_path)[0]
        output_file_path = base_name + ".json"
        result = csv_to_json(csv_file_path, output_file_path)
        print(result)
    else:
        print("Please provide either a single file (-f) or a directory (-b).")

if __name__ == "__main__":
    main()
    