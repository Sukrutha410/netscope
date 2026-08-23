# NetScope — Network Scanner Dashboard

A lightweight network monitoring tool that scans your local network, stores scan history, and displays results in a web dashboard — with automatic new-device detection.

## Features
- 🔍 **Network scanning** — uses `nmap` to discover live hosts on the local subnet
- 💾 **Scan history** — every scan is saved as structured JSON, building a timeline over time
- 🌐 **Web dashboard** — Flask-based UI showing IP, MAC address, and hostname for each device
- 🆕 **New device detection** — automatically highlights devices that weren't present in the previous scan
- 📜 **History browser** — view any past scan via a dropdown, not just the latest
- ⏰ **Automated scanning** — runs on a schedule via cron, no manual clicks needed
- ▶️ **Manual scan trigger** — "Scan Now" button to scan on demand from the browser

## Tech Stack
- Python 3
- Flask
- nmap
- JSON (for lightweight persistent storage)
- cron (for scheduled scanning)

## How It Works
1. `scan.py` runs `nmap -sn <subnet>` to discover live hosts, parses the XML output, and appends results to `scan_history.json`
2. `dashboard.py` (Flask app) reads that history and renders it as an HTML table
3. Comparing consecutive scans flags any newly appeared IP address
4. A cron job runs `scan.py` every 5 minutes to keep history up to date automatically

## Setup

```bash
git clone <your-repo-url>
cd netscope
python3 -m venv venv
source venv/bin/activate
pip install flask

# One-time: allow nmap to run without a sudo password prompt
sudo visudo
# add this line (replace with your username):
# yourusername ALL=(ALL) NOPASSWD: /usr/bin/nmap

python3 dashboard.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Optional: Automated Scanning

Add to crontab (`crontab -e`) to scan every 5 minutes:
## Screenshots
*(add a screenshot of your dashboard here)*

## Future Improvements
- Port scanning per host (not just host discovery)
- Email/notification alerts on new device detection
- Charts showing device count over time
- Basic authentication for the dashboard

## Disclaimer
Only scan networks you own or have explicit permission to scan.

## Author
Sukrutha — built as part of a self-directed cybersecurity learning path (Linux, networking, Python fundamentals).

Cron line (add via `crontab -e`):
*/5 * * * * /usr/bin/python3 /home/sukrutha-s/netscope/scan.py >> /home/sukrutha-s/netscope/scan.log 2>&1
