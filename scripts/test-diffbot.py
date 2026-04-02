"""Test Diffbot API — extract content from a website.

Usage:
  python3.13 scripts/test-diffbot.py                              # Default: extract from google-ad-automation.jytech.us
  python3.13 scripts/test-diffbot.py https://example.com          # Extract from custom URL
  python3.13 scripts/test-diffbot.py https://example.com analyze  # Extract + analyze for ad optimization
"""
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

# Load .env.local
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

DIFFBOT_TOKEN = os.environ.get('DIFFBOT_API_TOKEN', '')

if not DIFFBOT_TOKEN:
    print('Error: DIFFBOT_API_TOKEN not set in .env.local')
    sys.exit(1)


def extract_article(url: str) -> dict:
    """Extract article/page content using Diffbot Analyze API."""
    params = urllib.parse.urlencode({
        'token': DIFFBOT_TOKEN,
        'url': url,
    })
    api_url = f'https://api.diffbot.com/v3/analyze?{params}'

    print(f'Extracting content from: {url}')
    print(f'Using Diffbot Analyze API...\n')

    req = urllib.request.Request(api_url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f'Error ({e.code}): {body}')
        sys.exit(1)


def print_results(data: dict):
    """Pretty print extracted content."""
    print('=' * 60)
    print(f'Title: {data.get("title", "N/A")}')
    print(f'Type: {data.get("type", "N/A")}')
    print(f'URL: {data.get("pageUrl", data.get("resolvedPageUrl", "N/A"))}')
    print('=' * 60)

    objects = data.get('objects', [])
    if not objects:
        print('\nNo structured content extracted.')
        print(f'\nRaw response keys: {list(data.keys())}')
        return

    for i, obj in enumerate(objects):
        print(f'\n--- Object {i + 1} ({obj.get("type", "unknown")}) ---')
        print(f'Title: {obj.get("title", "N/A")}')

        text = obj.get('text', '')
        if text:
            preview = text[:500] + ('...' if len(text) > 500 else '')
            print(f'Text ({len(text)} chars):\n{preview}')

        # Tags / categories
        tags = obj.get('tags', [])
        if tags:
            tag_labels = [t.get('label', '') for t in tags[:10]]
            print(f'Tags: {", ".join(tag_labels)}')

        # Images
        images = obj.get('images', [])
        if images:
            print(f'Images: {len(images)}')
            for img in images[:3]:
                print(f'  - {img.get("url", "N/A")}')

        # Links
        links = obj.get('links', [])
        if links:
            print(f'Links: {len(links)}')

        # Meta
        meta = obj.get('meta', {})
        if meta:
            desc = meta.get('description', '')
            if desc:
                print(f'Meta description: {desc}')

    return objects


def analyze_for_ads(objects: list, url: str):
    """Analyze extracted content for Google Ads optimization."""
    print('\n' + '=' * 60)
    print('AD OPTIMIZATION ANALYSIS')
    print('=' * 60)

    all_text = ' '.join(obj.get('text', '') for obj in objects)
    all_tags = []
    for obj in objects:
        all_tags.extend([t.get('label', '') for t in obj.get('tags', [])])

    titles = [obj.get('title', '') for obj in objects if obj.get('title')]

    print(f'\nPage: {url}')
    print(f'Total content length: {len(all_text)} characters')
    print(f'Number of sections: {len(objects)}')

    if titles:
        print(f'\nHeadings found:')
        for t in titles[:10]:
            print(f'  - {t}')

    if all_tags:
        unique_tags = list(set(all_tags))[:15]
        print(f'\nSuggested keywords from content:')
        for tag in unique_tags:
            print(f'  - {tag}')

    # Simple keyword extraction from text
    if all_text:
        words = all_text.lower().split()
        word_freq = {}
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'shall', 'can', 'and', 'but', 'or', 'nor',
                      'not', 'so', 'yet', 'both', 'either', 'neither', 'each', 'every',
                      'all', 'any', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                      'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about',
                      'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
                      'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
                      'once', 'here', 'there', 'when', 'where', 'why', 'how', 'this', 'that',
                      'these', 'those', 'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he',
                      'she', 'it', 'they', 'them', 'their', 'what', 'which', 'who', 'whom',
                      'up', '—', '-', '|', '&', 'its'}
        for word in words:
            word = word.strip('.,!?;:()[]{}"\'-')
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        print(f'\nTop keywords by frequency:')
        for word, count in top_words:
            print(f'  {word}: {count}x')

    print(f'\nRecommendations:')
    print(f'  1. Use top keywords in Google Ads headlines and descriptions')
    print(f'  2. Create ad groups around the main content themes')
    print(f'  3. Use extracted headings as responsive search ad headlines')
    print(f'  4. Target tags as keywords in your campaigns')


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://google-ad-automation.jytech.us'
    analyze = len(sys.argv) > 2 and sys.argv[2] == 'analyze'

    data = extract_article(url)
    objects = print_results(data)

    if analyze and objects:
        analyze_for_ads(objects, url)
    elif not analyze:
        print(f'\nTip: Run with "analyze" flag for ad optimization suggestions:')
        print(f'  python3.13 scripts/test-diffbot.py {url} analyze')


if __name__ == '__main__':
    main()
