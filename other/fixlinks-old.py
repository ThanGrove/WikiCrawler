import os
import re
from functools import reduce


# --- CONFIG ---
FOLDER = "fiscaltibet"  # ← change this to your folder path
ENCODING = "utf-8"

# --- PREP ---
# Get all .html filenames in the folder
filenames = [f for f in os.listdir(FOLDER) if f.lower().endswith(".html")]
# Make bak folder for old versions
bakfolder = os.path.join(FOLDER, 'bak')
os.makedirs(bakfolder, exist_ok=True)

# Map lowercase -> actual filename
filemap = {f.lower(): f for f in filenames}
# entities where the percent sign becomes %25. like %2520
old_list = [
    '%20'
]
new_list = [s.replace('%', '%25') for s in old_list]  # auto double-encode

filemap = {
    **filemap,
    **{
        reduce(lambda key, pair: key.replace(*pair), zip(old_list, new_list), k): v
        for k, v in filemap.items()
    },
}

# Old version: filemap = {**filemap, **{k.replace('%20', '%2520'): v for k, v in filemap.items()}}

# Regex to find href="filename.html" or href='filename.html'
href_pattern = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

for fname in filenames:
    fpath = os.path.join(FOLDER, fname)

    with open(fpath, "r", encoding=ENCODING, errors="ignore") as f:
        html = f.read()

    def replace_href(match):
        href = match.group(1)
        href_lower = href.lower()

        # Only fix local HTML links (no http:// etc.)
        if href_lower.endswith(".html") and not re.match(r'^[a-z]+://', href_lower):
            # Normalize path (handle subfolders if any)
            target = os.path.basename(href_lower)
            prefix = os.path.dirname(href)
            if target in filemap:
                correct_name = filemap[target]
                corrected_href = os.path.join(prefix, correct_name) if prefix else correct_name
                # corrected_href = corrected_href.replace('%20', '%2520')
                if corrected_href != href:
                    nonlocal_change[0] = True
                    print(f"[{fname}] fixing link: {href} → {corrected_href}")
                    return f'href="{corrected_href}"'
        return match.group(0)

    nonlocal_change = [False]
    new_html = href_pattern.sub(replace_href, html)
    changed = nonlocal_change[0]

    if changed:
        backpath = os.path.join(bakfolder, fname) + ".bak"
        with open(backpath, "w", encoding=ENCODING) as f:
            f.write(new_html)
        print(f"Updated {fname} (backup saved as {backpath})")

print("Done!")
