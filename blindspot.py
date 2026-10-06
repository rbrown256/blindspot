#!/usr/bin/env python3
import sys
import urllib.request
import urllib.error
import urllib.parse
import urllib.robotparser
from html.parser import HTMLParser

class IndexabilityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots_directives = []
        self.canonical_url = None

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attrs_dict = dict(attrs)
            name = attrs_dict.get('name', '').lower()
            if name in ['robots', 'googlebot']:
                content = attrs_dict.get('content', '').lower()
                if content:
                    self.robots_directives.append(content)
        elif tag == 'link':
            attrs_dict = dict(attrs)
            rel = attrs_dict.get('rel', '').lower()
            if rel == 'canonical':
                self.canonical_url = attrs_dict.get('href', '')

def check_indexability(url):
    print(f"Analysing URL: {url}\n")
    
    # 1. Check robots.txt
    parsed_url = urllib.parse.urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        can_fetch = rp.can_fetch("*", url)
    except Exception:
        can_fetch = True
        
    print(f"Robots.txt allows crawling: {can_fetch}")
    if not can_fetch:
        print("  Result: Blocked by robots.txt")
    
    # 2. Fetch page and check headers/status
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (compatible; IndexCheckBot/1.0)'}
    )
    
    try:
        response = urllib.request.urlopen(req)
        status_code = response.getcode()
        headers = response.info()
        html_content = response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        status_code = e.code
        headers = e.headers
        html_content = e.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"\nError fetching URL: {e}")
        return
        
    print(f"\nHTTP Status Code: {status_code}")
    if status_code >= 400:
        print("  Result: Page may not be indexable due to error status code.")
        
    x_robots_tag = headers.get('X-Robots-Tag', '')
    print(f"\nX-Robots-Tag Header: {x_robots_tag if x_robots_tag else 'None'}")
    if x_robots_tag and 'noindex' in x_robots_tag.lower():
        print("  Result: Blocked by X-Robots-Tag")
        
    # 3. Check HTML tags
    parser = IndexabilityParser()
    parser.feed(html_content)
    
    print("\nMeta Robots Tags:")
    if parser.robots_directives:
        for directive in parser.robots_directives:
            print(f"  {directive}")
            if 'noindex' in directive:
                print("  Result: Blocked by meta robots tag")
    else:
        print("  None")
        
    print("\nCanonical URL:")
    if parser.canonical_url:
        print(f"  {parser.canonical_url}")
        if parser.canonical_url.strip('/') != url.strip('/'):
            print("  Result: Canonical URL differs from requested URL. This page might not be indexed as the primary version.")
    else:
        print("  None")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./blind-spot.py ")
        sys.exit(1)
    target_url = sys.argv[1]
    check_indexability(target_url)
