import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.parse

visited_pages = set()
visited_assets = set()
deepest = 0
links_skipped = set()


def safe_filename(url):
    """Generate a filesystem-safe filename for a URL."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path or path.endswith('/'):
        path += 'index.html'
    filename = path.replace('/', '_')
    return filename


def download_asset(url, base_domain, assets_dir):
    """Download a single asset (image, CSS, JS)."""
    if url in visited_assets:
        return None
    visited_assets.add(url)

    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != base_domain:
        return None  # skip external assets

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
    except Exception as e:
        print(f"  [!] Asset error {url}: {e}")
        return None

    # Save asset
    os.makedirs(assets_dir, exist_ok=True)
    local_name = safe_filename(url)
    asset_path = os.path.join(assets_dir, local_name)
    with open(asset_path, 'wb') as f:
        f.write(r.content)
    return os.path.relpath(asset_path, assets_dir)

def rewrite_internal_link(href):
    """
    Rewrite an internal UVA Collab /wiki/... link into a local relative filename.
    Example:
      '/wiki/tibetan-script/Using%20Tibetan%20in%20Linux.html'
      -> './wiki_tibetan-script_Using%2520Tibetan%2520in%2520Linux.html'
    """
    if href.startswith('/wiki/'):
        # Replace % with %25 to preserve encoding safely
        href = href.replace('%', '%25')
        # Replace slashes with underscores and add leading './'
        href = './' + href.lstrip('/').replace('/', '_')
    return href

def crawl(url, base_domain, base_path, output_dir='site_download', depth=0, max_depth=2):
    global deepest, links_skipped
    # print(f"base domain: {base_domain}") = collab.its.virginia.edu
    """Recursively crawl and save pages plus linked assets."""
    if depth > max_depth or url in visited_pages:
        return

    if depth > deepest:
        deepest = depth

    visited_pages.add(url)

    print(f"{'  ' * depth}Level {depth}: {url}")
    try:
        # Copy the cookie from your browser
        cookies = {
            "JSESSIONID": "c2c6df62-1fc1-4ff5-9098-d4c37a750a2e.collab20-prod-orange.6.iolpujd4xlwx2c62ptsuvlpxn"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }
        r = requests.get(url, cookies=cookies, headers=headers, timeout=10)
        if r.status_code != 200 or 'text/html' not in r.headers.get('content-type', ''):
            return
    except Exception as e:
        print(f"{'  ' * depth}Error fetching {url}: {e}")
        return

    # Prepare directories
    os.makedirs(output_dir, exist_ok=True)
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Parse HTML
    soup = BeautifulSoup(r.text, 'html.parser')

    # Download linked assets
    for tag, attr in [('img', 'src'), ('link', 'href'), ('script', 'src')]:
        for node in soup.find_all(tag):
            if node.has_attr(attr):
                asset_url = urljoin(url, node[attr])
                local_asset = download_asset(asset_url, base_domain, assets_dir)
                if local_asset:
                    node[attr] = os.path.join('assets', safe_filename(asset_url))

    # Save HTML page
    page_filename = safe_filename(url)
    page_path = os.path.join(output_dir, page_filename)

    # Follow links
    for link_tag in soup.find_all('a', href=True):
        original_href = link_tag['href']
        # print(f"Original href: {original_href}")
        absolute_link = urljoin(url, original_href)
        parsed_link = urlparse(absolute_link)

        # Only rewrite and crawl same-domain links
        if parsed_link.netloc == base_domain:
            # print(f'parsed path is: {parsed_link.path}')
            if parsed_link.path.startswith(base_path):
                # print(f"It starts with: {base_path}")
                # Rewrite href for local storage
                new_href = rewrite_internal_link(parsed_link.path)
                link_tag['href'] = new_href
                crawl(absolute_link, base_domain, base_path, output_dir, depth + 1, max_depth)
            else:
                links_skipped.add(absolute_link)

    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    time.sleep(0.5)  # Be polite


if __name__ == "__main__":
    collab_name = 'av-thl'
    start_url = f"https://collab.its.virginia.edu/wiki/{collab_name}/home.html"
    base_domain = urlparse(start_url).netloc
    base_path = f'/wiki/{collab_name}'
    crawl(start_url, base_domain, base_path, collab_name, max_depth=100)
    print(f"Maximum achieved depth reached: {deepest}")
    outfile = os.path.join(collab_name, 'skipped-links.txt')
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(str(links_skipped))

