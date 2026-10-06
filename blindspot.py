#!/usr/bin/env python3

import sys
import argparse
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

def check_indexability(url, show_robots):
    print(f"\n[+] Analysing URL: {url}\n")
    
    is_hidden = False
    hidden_reasons = []

    # Use a standard Browser UA to prevent WAFs/Cloudflare from auto-blocking the script with a 403
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

    # 1. Check robots.txt
    parsed_url = urllib.parse.urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    
    robots_content = None
    try:
        # We fetch manually instead of rp.read() to avoid Python's default User-Agent triggering a 403
        rb_req = urllib.request.Request(robots_url, headers={'User-Agent': USER_AGENT})
        rb_response = urllib.request.urlopen(rb_req, timeout=10)
        robots_content = rb_response.read().decode('utf-8', errors='ignore')
        
        # Feed the manually fetched content into the robot parser
        rp.parse(robots_content.splitlines())
        can_fetch = rp.can_fetch("*", url)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            # If robots.txt itself is actively forbidden, assume it's blocked
            can_fetch = False
            robots_content = f"[HTTP {e.code}: Access Denied to robots.txt]"
        else:
            # For 404s or 500s on the robots file, standard practice allows crawling
            can_fetch = True
            robots_content = f"[HTTP {e.code}: robots.txt not found]"
    except Exception as e:
        can_fetch = True
        robots_content = f"[Error fetching robots.txt: {e}]"
        
    print(f"[*] Robots.txt allows crawling: {can_fetch}")
    if not can_fetch:
        print("    -> Result: Blocked by robots.txt")
        is_hidden = True
        hidden_reasons.append("Blocked by robots.txt")
        
    # Output robots.txt contents if the option is passed
    if show_robots:
        print(f"\n--- Contents of {robots_url} ---")
        if robots_content and robots_content.strip():
            print(robots_content.strip())
        else:
            print("[File is empty]")
        print("-" * (32 + len(robots_url)) + "\n")

    # 2. Fetch page and check headers/status
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    
    try:
        response = urllib.request.urlopen(req, timeout=15)
        status_code = response.getcode()
        headers = response.info()
        html_content = response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        status_code = e.code
        headers = e.headers
        html_content = e.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"\n[!] Error fetching URL: {e}")
        is_hidden = True
        hidden_reasons.append(f"Connection Error: {e}")
        show_final_result(is_hidden, hidden_reasons)
        return
        
    print(f"\n[*] HTTP Status Code: {status_code}")
    if status_code >= 400:
        print("    -> Result: Page may not be indexable due to error status code.")
        is_hidden = True
        hidden_reasons.append(f"HTTP Status {status_code} Error")
        
    x_robots_tag = headers.get('X-Robots-Tag', '')
    print(f"\n[*] X-Robots-Tag Header: {x_robots_tag if x_robots_tag else 'None'}")
    if x_robots_tag and 'noindex' in x_robots_tag.lower():
        print("    -> Result: Blocked by X-Robots-Tag")
        is_hidden = True
        hidden_reasons.append("X-Robots-Tag Header contains 'noindex'")
        
    # 3. Check HTML tags
    parser = IndexabilityParser()
    parser.feed(html_content)
    
    print("\n[*] Meta Robots Tags:")
    if parser.robots_directives:
        for directive in parser.robots_directives:
            print(f"    - {directive}")
            if 'noindex' in directive:
                print("    -> Result: Blocked by meta robots tag")
                is_hidden = True
                if "Meta robots tag contains 'noindex'" not in hidden_reasons:
                    hidden_reasons.append("Meta robots tag contains 'noindex'")
    else:
        print("    - None")
        
    print("\n[*] Canonical URL:")
    if parser.canonical_url:
        print(f"    - {parser.canonical_url}")
        if parser.canonical_url.strip('/') != url.strip('/'):
            print("    -> Result: Canonical URL differs from requested URL. This page might not be indexed as the primary version.")
    else:
        print("    - None")

    # Final Result
    show_final_result(is_hidden, hidden_reasons)


def show_final_result(is_hidden, hidden_reasons):
    print("\n" + "="*50)
    print("                 FINAL RESULT")
    print("="*50)
    
    if is_hidden:
        print("\n[ STATUS : HIDDEN ]")
        print("Reasons:")
        for reason in hidden_reasons:
            print(f" x {reason}")
            
        # 200% Cooler Ninja ASCII art (Hidden)
        ninja_art = r"""
              ()       ()
               \       /
                \     /
                 \   /
               ___\_/___
             /'         '\    ~,
            |  =========  |  ~'
            |  (O)   (O)  |~'
            |  =========  |
             \,_________./
               |       |
               |       |
               
      [ TARGET IS CONCEALED IN THE SHADOWS ]
        """
        print(ninja_art)
    else:
        print("\n[ STATUS : NOT HIDDEN (INDEXABLE) ]")
        print("No direct blockers found. The page is clear for indexing.")
        
        # 200% Cooler Eye ASCII art (Not Hidden)
        eye_art = r"""
                 .____.
           _.---'      '---._
         .'                  '.
        /  .-'    ____    '-.  \
       /  /      /    \      \  \
      |  |      |  ()  |      |  |
       \  \      \____/      /  /
        \  '-.__        __.-'  /
         '.     `""""""`     .'
           '---.________.---'
           
      [ TARGET IS FULLY EXPOSED TO THE WEB ]
        """
        print(eye_art)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Check URL indexability and blocking factors.")
    arg_parser.add_argument("url", help="The target URL to check")
    arg_parser.add_argument("--show-robots", "-r", action="store_true", help="Output the contents of robots.txt")
    
    args = arg_parser.parse_args()
    check_indexability(args.url, args.show_robots)
