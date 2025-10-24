import os
import re
import shutil

# Set the folder path
folder_path = 'av-thl'
bak_path = os.path.join(folder_path, 'originals')
os.makedirs(bak_path, exist_ok=True)

def normalizeHrefs(strval):
    replacements = {
        '%20': '-',
        '%2520': '-',
        '%26': 'n',
        '%2526': 'n',
        '---': '--',
    }
    for old, new in replacements.items():
        strval = strval.replace(old, new)
    return strval.lower()

# Iterate over each file in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    file_bak_path = os.path.join(bak_path, filename)

    # Make sure it's a file
    if os.path.isfile(file_path) and filename.startswith('wiki'):
        # Open and read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to find href values (inside quotes)
        pattern = r'href="([^"]*)"'

        # Replace each href with the processed value
        def replacer(match):
            original_url = match.group(1)
            new_url = normalizeHrefs(original_url)
            return f'href="{new_url}"'

        new_content = re.sub(pattern, replacer, content)
        new_filename = normalizeHrefs(filename)

        shutil.move(file_path, file_bak_path)
        new_path = os.path.join(folder_path, new_filename)
        # Write the updated content back to the file
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Processed {filename}")
