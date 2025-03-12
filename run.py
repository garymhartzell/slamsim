import subprocess
import os

def run_script(script_name):
    result = subprocess.run(['python', script_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{script_name} executed successfully.")
    else:
        print(f"Error executing {script_name}:\n{result.stderr}")

def main():
    # Set base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = [
        os.path.join(base_dir, 'bin/gen_wrestlers.py'),
        os.path.join(base_dir, 'bin/gen_tagteams.py'),
        os.path.join(base_dir, 'bin/gen_roster.py'),
        os.path.join(base_dir, 'bin/gen_events.py'),
        os.path.join(base_dir, 'bin/gen_events2.py'),
        os.path.join(base_dir, 'bin/gen_news.py'),
        os.path.join(base_dir, 'bin/gen_index.py'),
    ]
    
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main()
