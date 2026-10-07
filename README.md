# Blindspot 🥷👁️

**Blindspot** is a lightweight, zero-dependency command-line tool that analyzes web pages to determine if they are hidden from search engines. It thoroughly checks for indexing blockers across the `robots.txt` file, HTTP headers, HTML meta tags, and canonical links.

If a page is hidden, Blindspot will tell you exactly *why* it's hiding in the shadows.

## ✨ Features

- **Zero Dependencies:** Built entirely with Python 3 standard libraries. No `pip install` required.
- **WAF Evasion:** Uses standard browser User-Agents to fetch `robots.txt` and page contents, preventing false positives from hosts like Cloudflare blocking default Python HTTP requests.
- **Deep Inspection:**
  - Evaluates `robots.txt` rules for the specific URL.
  - Checks HTTP Status Codes (flags 400+ errors).
  - Scans HTTP Headers for `X-Robots-Tag: noindex`.
  - Parses HTML for `<meta name="robots" content="noindex">`.
  - Identifies Canonical URL mismatches.
- **Raw Output:** View the target's raw `robots.txt` directly in the terminal using the `--show-robots` flag.
- **Rad ASCII Art:** Delivers the final verdict with 200% cooler terminal art. 

## 🚀 Installation

Just clone the repository (or download the script) and make it executable:

```bash
git clone --depth=1 https://github.com/rbrown256/blindspot
cd blindspot
chmod +x blindspot.py
```

## 💻 Usage

Run the script and pass the target URL as an argument:

```bash
./blindspot.py https://example.com
```

### Options

| Flag | Short | Description |
| :--- | :---: | :--- |
| `--show-robots` | `-r` | Fetches and prints the full contents of the site's `robots.txt` file during analysis. |
| `--help` | `-h` | Displays the help menu. |

**Example with flags:**
```bash
./blindspot.py https://example.com/secret-page -r
```

## 🔍 Example Output

### When a page is hidden:
```text
[+] Analysing URL: https://example.com/wp-admin/

[*] Robots.txt allows crawling: False
    -> Result: Blocked by robots.txt

[*] HTTP Status Code: 200

[*] X-Robots-Tag Header: None

[*] Meta Robots Tags:
    - noindex, nofollow
    -> Result: Blocked by meta robots tag

==================================================
                 FINAL RESULT
==================================================

[ STATUS : HIDDEN ]
Reasons:
 x Blocked by robots.txt
 x Meta robots tag contains 'noindex'

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
```

### When a page is indexable:
```text
==================================================
                 FINAL RESULT
==================================================

[ STATUS : NOT HIDDEN (INDEXABLE) ]
No direct blockers found. The page is clear for indexing.

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
```

## 🛠️ Requirements

- Python 3.6+
- Internet connection 

## 📄 License

This project is open-source and available under the MIT License.


