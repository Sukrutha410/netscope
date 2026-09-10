import subprocess
import xml.etree.ElementTree as ET
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from config import SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL

def run_scan(subnet="192.168.221.0/24"):
    print(f"Scanning {subnet}...")
    
    result = subprocess.run(
        ["sudo", "nmap", "-sn", subnet, "-oX", "-"],
        capture_output=True,
        text=True
    )
    
    return result.stdout

def scan_ports(ip):
    """Scan common ports on a single host and return open ones."""
    result = subprocess.run(
        ["sudo", "nmap", "-sV", "--top-ports", "20", ip, "-oX", "-"],
        capture_output=True,
        text=True
    )
    
    ports = []
    try:
        root = ET.fromstring(result.stdout)
        host = root.find("host")
        if host is not None:
            ports_elem = host.find("ports")
            if ports_elem is not None:
                for port in ports_elem.findall("port"):
                    state = port.find("state").get("state")
                    if state == "open":
                        service_elem = port.find("service")
                        service_name = service_elem.get("name") if service_elem is not None else "unknown"
                        ports.append({
                            "port": port.get("portid"),
                            "protocol": port.get("protocol"),
                            "service": service_name
                        })
    except ET.ParseError:
        pass
    
    return ports

def parse_hosts(xml_data):
    root = ET.fromstring(xml_data)
    hosts = []
    
    for host in root.findall("host"):
        status = host.find("status").get("state")
        if status != "up":
            continue
        
        ip = host.find("address").get("addr")
        
        mac = None
        mac_elem = host.find("address[@addrtype='mac']")
        if mac_elem is not None:
            mac = mac_elem.get("addr")
        
        hostname = None
        hostnames = host.find("hostnames")
        if hostnames is not None and hostnames.find("hostname") is not None:
            hostname = hostnames.find("hostname").get("name")
        
        print(f"  Scanning ports on {ip}...")
        ports = scan_ports(ip)
        
        hosts.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "ports": ports,
            "scanned_at": datetime.now().isoformat()
        })
    
    return hosts

def save_results(hosts, filename="scan_history.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            history = json.load(f)
    else:
        history = []
    
    scan_entry = {
        "scan_time": datetime.now().isoformat(),
        "hosts": hosts
    }
    history.append(scan_entry)
    
    with open(filename, "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"Saved scan to {filename} ({len(history)} scans total in history)")
    
    return history

def find_new_devices(history):
    """Compare the latest scan to the previous one, return list of new IPs."""
    if len(history) < 2:
        return []
    
    latest_ips = {h["ip"] for h in history[-1]["hosts"]}
    previous_ips = {h["ip"] for h in history[-2]["hosts"]}
    
    new_ips = latest_ips - previous_ips
    
    # Return full host info for new IPs, not just the IP string
    new_hosts = [h for h in history[-1]["hosts"] if h["ip"] in new_ips]
    return new_hosts

def send_alert_email(new_hosts):
    """Send an email listing newly detected devices."""
    body_lines = ["NetScope detected new device(s) on your network:\n"]
    for h in new_hosts:
        body_lines.append(f"- IP: {h['ip']} | MAC: {h['mac'] or 'N/A'} | Hostname: {h['hostname'] or 'Unknown'}")
    body = "\n".join(body_lines)
    
    msg = MIMEText(body)
    msg["Subject"] = f"NetScope Alert: {len(new_hosts)} new device(s) detected"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print(f"Alert email sent for {len(new_hosts)} new device(s).")
    except Exception as e:
        print(f"Failed to send alert email: {e}")

if __name__ == "__main__":
    xml_output = run_scan()
    hosts = parse_hosts(xml_output)
    
    print(f"\nFound {len(hosts)} live hosts:\n")
    for h in hosts:
        print(h)
    
    history = save_results(hosts)
    
    new_hosts = find_new_devices(history)
    if new_hosts:
        print(f"\n{len(new_hosts)} new device(s) detected — sending alert email...")
        send_alert_email(new_hosts)
    else:
        print("\nNo new devices detected.")
