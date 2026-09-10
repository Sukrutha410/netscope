from flask import Flask, render_template, redirect, url_for, request
import json
import os
from scan import run_scan, parse_hosts, save_results, find_new_devices, send_alert_email

app = Flask(__name__)

def load_history():
    filename = "scan_history.json"
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)

def get_new_devices(history, index):
    if index < 1:
        return set()
    
    current_ips = {h["ip"] for h in history[index]["hosts"]}
    previous_ips = {h["ip"] for h in history[index - 1]["hosts"]}
    
    return current_ips - previous_ips

def get_chart_data(history):
    labels = []
    device_counts = []
    
    for entry in history:
        labels.append(entry["scan_time"])
        device_counts.append(len(entry["hosts"]))
    
    return {"labels": labels, "counts": device_counts}

@app.route("/")
def index():
    history = load_history()
    if not history:
        return render_template("index.html", scan=None, new_ips=set(), history=[], selected_index=None, chart_data=None)
    
    selected_index = request.args.get("scan", type=int)
    if selected_index is None or selected_index < 0 or selected_index >= len(history):
        selected_index = len(history) - 1
    
    scan = history[selected_index]
    new_ips = get_new_devices(history, selected_index)
    chart_data = get_chart_data(history)
    
    return render_template(
        "index.html",
        scan=scan,
        new_ips=new_ips,
        history=history,
        selected_index=selected_index,
        chart_data=chart_data
    )

@app.route("/scan", methods=["POST"])
def scan_now():
    xml_output = run_scan()
    hosts = parse_hosts(xml_output)
    history = save_results(hosts)
    
    new_hosts = find_new_devices(history)
    if new_hosts:
        send_alert_email(new_hosts)
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
