# NetScope — Network Scanner Dashboard

A lightweight network monitoring tool that scans your local network, stores scan history, and displays results in a web dashboard — with automatic new-device detection, per-host port scanning, and trend charts.

## Features
- 🔍 **Network scanning** — uses `nmap` to discover live hosts on the local subnet
- 🔓 **Port scanning per host** — checks top 20 common ports on each device and identifies running services (e.g., DNS, HTTP, SSH)
- 💾 **Scan history** — every scan is saved as structured JSON, building a timeline over time
- 🌐 **Web dashboard** — Flask-based UI showing IP, MAC address, hostname, and open ports for each device
- 🆕 **New device detection** — automatically highlights devices that weren't present in the previous scan
- 📜 **History browser** — view any past scan via a dropdown, not just the latest
- 📊 **Trend chart** — visualizes device count over time using Chart.js
- ⏰ **Automated scanning** — runs on a schedule via cron, no manual clicks needed
- ▶️ **Manual scan trigger** — "Scan Now" button to scan on demand from the browser

## Tech Stack
- Python 3
- Flask
- nmap
- JSON (for lightweight persistent storage)
- Chart.js (for data visualization)
- cron (for scheduled scanning)

## How It Works
1. `scan.py` runs `nmap -sn <subnet>` to discover live hosts, then runs a second `nmap -sV --top-ports 20` scan per host to detect open ports and services
2. Results are parsed from nmap's XML output and appended to `scan_history.json`
3. `dashboard.py` (Flask app) reads that history and renders it as an HTML table, plus a Chart.js line graph of device count over time
4. Comparing consecutive scans flags any newly appeared IP address
5. A cron job runs `scan.py` every 5 minutes to keep history up to date automatically

## Setup

```bash
git clone https://github.com/Sukrutha410/netscope.git
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

## Future Improvements
- Email/notification alerts on new device detection
- Basic authentication for the dashboard
- Deploy with a production WSGI server (gunicorn)

## Disclaimer
Only scan networks you own or have explicit permission to scan.

## Author
Sukrutha — built as part of a self-directed cybersecurity learning path (Linux, networking, Python fundamentals).

## Email Alerts
NetScope sends an email notification whenever a new device is detected on the network, whether triggered manually, via the dashboard, or through the automated cron scan. Requires a `config.py` file (not included, gitignored) with:
Uses a Gmail App Password (not your real password) for secure SMTP authentication.
