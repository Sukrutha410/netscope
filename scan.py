import subprocess
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

def run_scan(subnet="192.168.221.0/24"):
    print(f"Scanning {subnet}...")
    
    result = subprocess.run(
        ["sudo", "nmap", "-sn", subnet, "-oX", "-"],
        capture_output=True,
        text=True
    )
    
    return result.stdout

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
        
        hosts.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "scanned_at": datetime.now().isoformat()
        })
    
    return hosts

def save_results(hosts, filename="scan_history.json"):
    # Load existing history if file exists
    if os.path.exists(filename):
        with open(filename, "r") as f:
            history = json.load(f)
    else:
        history = []
    
    # Add this scan as a new entry
    scan_entry = {
        "scan_time": datetime.now().isoformat(),
        "hosts": hosts
    }
    history.append(scan_entry)
    
    # Save back to file
    with open(filename, "w") as f:
        json.dump(history, f, indent=2)
    
    print(f"Saved scan to {filename} ({len(history)} scans total in history)")

if __name__ == "__main__":
    xml_output = run_scan()
    hosts = parse_hosts(xml_output)
    
    print(f"\nFound {len(hosts)} live hosts:\n")
    for h in hosts:
        print(h)
    
    save_results(hosts)
