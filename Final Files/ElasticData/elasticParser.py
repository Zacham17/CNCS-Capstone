import json
from collections import defaultdict
from datetime import datetime, timedelta

# Function to convert bytes to megabytes
def bytes_to_megabytes(bytes):
    return round(bytes / (1024 * 1024), 2)

# Function to convert bytes to data transfer rate
def bytes_to_data_transfer_rate(bytes):
    return round(bytes / (1024 * 1024), 2)

# Function to convert milliseconds to days, hours, minutes, and seconds
def ms_to_seconds(ms):
    seconds = ms // 1000
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

# Function to convert percentage to decimal
def convert_to_percentage(value):
    return f"{round(value * 100, 2)}%"

# Function to parse data from Auditbeat index
def parse_auditbeat(data):
    host_info = {}

    # Standard Linux users
    standard_users = [
        "daemon", "bin", "sys", "sync", "games", "man", "lp", "mail", "news",
        "uucp", "proxy", "www-data", "backup", "list", "irc", "_apt", "nobody",
        "systemd-network", "mysql", "tss", "strongswan", "systemd-timesync",
        "redsocks", "rwhod", "_gophish", "iodine", "messagebus", "miredo",
        "redis", "usbmux", "mosquitto", "tcpdump", "sshd", "_rpc", "dnsmasq",
        "statd", "avahi", "stunnel4", "Debian-snmp", "_gvm", "speech-dispatcher",
        "sslh", "postgres", "pulse", "inetsim", "lightdm", "geoclue", "saned",
        "polkitd", "rtkit", "colord", "nm-openvpn", "nm-openconnect",
        "landscape", "fwupd-refresh", "systemd-resolve", "gnats", "pollinate",
        "syslog", "uuidd", "lxd"
    ]

    for item in data:
        if "_source" in item:
            source = item["_source"]
            host_name = source.get("host", {}).get("name", "")
            user_name = source.get("user", {}).get("name", "")
            process_name = source.get("process", {}).get("name", "")
            message = source.get("message", "")
            
            if host_name:
                if host_name not in host_info:
                    host_info[host_name] = {"Users": set(), "Unique Processes": set(), "Uptime": "", "OS Distribution": ""}
                
                # Exclude standard Linux users
                if user_name and user_name not in standard_users:
                    host_info[host_name]["Users"].add(user_name)
                
                if "Ubuntu host" in message:
                    uptime = message.split("is up for ")[1].strip()
                    host_info[host_name]["Uptime"] = uptime

                if process_name:
                    host_info[host_name]["Unique Processes"].add(process_name)

                # Extract OS Distribution
                os_name = source.get("host", {}).get("os", {}).get("name", "")
                os_version = source.get("host", {}).get("os", {}).get("version", "")
                host_info[host_name]["OS Distribution"] = f"{os_name} {os_version}"

    # Convert sets to lists for better display
    for host in host_info:
        host_info[host]["Users"] = list(host_info[host]["Users"])
        host_info[host]["Unique Processes"] = len(host_info[host]["Unique Processes"])

    return host_info

from dateutil.parser import parse

# Function to parse data from Heartbeat index
def parse_heartbeat(data):
    down_services = {}
    most_recent_down_service = None
    up_services = {}

    for item in data:
        if "_source" in item:
            source = item["_source"]
            timestamp = source.get("@timestamp", "")
            summary = source.get("summary", {})
            status = summary.get("status", "")
            
            if status == "down":
                monitor_name = source.get("monitor", {}).get("name", "")
                if monitor_name:
                    down_services[monitor_name] = timestamp
                    if not most_recent_down_service or timestamp > most_recent_down_service:
                        most_recent_down_service = timestamp
            elif status == "up":
                monitor_name = source.get("monitor", {}).get("name", "")
                started_at = source.get("state", {}).get("started_at", "")
                if monitor_name:
                    up_services[monitor_name] = {"Timestamp": timestamp, "Started At": started_at}
                    
    # Calculate duration for up services
    for service, info in up_services.items():
        # Parse timestamp with timezone
        up_timestamp = parse(info["Timestamp"])
        started_at = parse(info["Started At"])
        
        duration = up_timestamp - started_at
        up_services[service]["Duration"] = ms_to_seconds(float(duration.total_seconds()) * 1000)

    return down_services, most_recent_down_service, up_services

# Function to parse data from Metricbeat index
def parse_metricbeat(data):
    monitored_hosts = {}

    for item in data:
        if "_source" in item:
            source = item["_source"]
            timestamp = source.get("@timestamp", "")
            host = source.get("host", {}).get("name", "")
            event = source.get("event", {})
            dataset = event.get("dataset", "")
            
            # Initialize all data dictionaries
            disk_utilization_data = {}
            memory_data = {}
            cpu_data = {}
            network_data = {}

            if dataset == "system.fsstat" or dataset == "system.filesystem":
                total_size = source.get("system", {}).get("fsstat", {}).get("total_size", {})
                free_size = total_size.get("free", "")
                used_size = total_size.get("used", "")
                
                if free_size == "" or used_size == "":
                    continue
                
                total_size_mb = bytes_to_megabytes(total_size.get("total", ""))
                free_size_mb = bytes_to_megabytes(free_size)
                used_size_mb = bytes_to_megabytes(used_size)
                
                disk_utilization = (used_size_mb / total_size_mb) * 100
                
                disk_utilization_data = {
                    "Total Disk Size (MB)": total_size_mb,
                    "Free Disk Size (MB)": free_size_mb,
                    "Used Disk Size (MB)": used_size_mb,
                    "Disk Utilization (%)": f"{round(disk_utilization, 2)}%"
                }
                
            elif dataset == "system.memory":
                memory = source.get("system", {}).get("memory", {})
                memory_used = memory.get("used", {}).get("bytes", "")
                memory_total = memory.get("total", "")
                
                if memory_used == "" or memory_total == "":
                    continue
                
                memory_used_mb = bytes_to_megabytes(memory_used)
                memory_total_mb = bytes_to_megabytes(memory_total)
                memory_utilization = (memory_used_mb / memory_total_mb) * 100
                
                memory_data = {
                    "Total Memory (MB)": memory_total_mb,
                    "Used Memory (MB)": memory_used_mb,
                    "Memory Utilization (%)": f"{round(memory_utilization, 2)}%"
                }
                
            elif dataset == "system.cpu":
                cpu_pct = source.get("system", {}).get("cpu", {}).get("total", {}).get("norm", {}).get("pct", "")
                
                if cpu_pct == "":
                    continue
                
                cpu_utilization = convert_to_percentage(float(cpu_pct))
                
                cpu_data = {
                    "CPU Utilization": cpu_utilization
                }
                
            elif dataset == "system.network":
                network_in_bytes = source.get("system", {}).get("network", {}).get("in", {}).get("bytes", "")
                network_out_bytes = source.get("system", {}).get("network", {}).get("out", {}).get("bytes", "")
                
                if network_in_bytes == "" or network_out_bytes == "":
                    continue
                
                inbound_traffic = bytes_to_data_transfer_rate(float(network_in_bytes))
                outbound_traffic = bytes_to_data_transfer_rate(float(network_out_bytes))
                
                network_data = {
                    "Inbound Network Traffic (MB)": inbound_traffic,
                    "Outbound Network Traffic (MB)": outbound_traffic
                }
                
            if host:
                if host not in monitored_hosts:
                    monitored_hosts[host] = {}
                
                monitored_hosts[host].update({
                    "Timestamp": datetime.fromisoformat(timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S"),
                    **disk_utilization_data,
                    **memory_data,
                    **cpu_data,
                    **network_data
                })

    return monitored_hosts

# Function to parse data from Filebeat index
def parse_filebeat(data):
    important_events = defaultdict(list)

    for item in data:
        if "_source" in item:
            source = item["_source"]
            process_name = source.get("process", {}).get("name", "")
            if process_name:
                timestamp = source.get("@timestamp", "")
                message = source.get("message", "")
                process = source.get("process", {})
                if process.get("name") == "systemd" and "Stopped" in message:
                    service_name = message.split("Stopped ")[1].strip(".")
                    important_events[(service_name, "Stopped")].append(timestamp)
                # Add more conditions for other important events here

    deduplicated_events = {}

    # For each event type, keep only the most recent timestamp and count duplicates
    for event, timestamps in important_events.items():
        most_recent = max(timestamps)
        duplicates = len(timestamps) - 1
        deduplicated_events[event] = {"Timestamp": most_recent, "Duplicates": duplicates}

    return deduplicated_events

# Read data from the JSON file
with open("queryData.json", "r") as file:
    data = json.load(file)

auditbeat_data = [item for item in data if item["_index"].startswith(".ds-auditbeat")]
heartbeat_data = [item for item in data if item["_index"].startswith(".ds-heartbeat")]
metricbeat_data = [item for item in data if item["_index"].startswith(".ds-metricbeat")]
filebeat_data = [item for item in data if item["_index"].startswith(".ds-filebeat")]

# Parse the data
auditbeat_results = parse_auditbeat(auditbeat_data)
down_services_count, _, up_services = parse_heartbeat(heartbeat_data)
metricbeat_results = parse_metricbeat(metricbeat_data)
filebeat_results = parse_filebeat(filebeat_data)

# Generate the output file
with open("output.txt", "w") as output_file:
    output_file.write("Auditbeat Results:\n")
    for host, details in auditbeat_results.items():
        output_file.write(f"Host: {host}\n")
        output_file.write(f"  Users: {', '.join(details['Users'])}\n")
        output_file.write(f"  Unique Processes: {details['Unique Processes']}\n")
        output_file.write(f"  OS Distribution: {details['OS Distribution']}\n")
        output_file.write(f"  Uptime: {details['Uptime']}\n")

    output_file.write("\n")
    output_file.write("Heartbeat Results:\n")
    output_file.write("Down Services: " + str(len(down_services_count)) + "\n")
    output_file.write("List of Down Services:\n")
    for service, timestamp in down_services_count.items():
        output_file.write(f"  {service}: Found down at {timestamp}\n")
    output_file.write("\nUp Services: " + str(len(up_services)) + "\n")
    output_file.write("List of Up Services and Duration:\n")
    for service, info in up_services.items():
        output_file.write(f"  {service}: Up since {info['Timestamp']} (Duration: {info['Duration']})\n")

    output_file.write("\n")
    output_file.write("Metricbeat Results:\n")
    for host, metrics in metricbeat_results.items():
        output_file.write(f"Host: {host}\n")
        for metric, value in metrics.items():
            output_file.write(f"  {metric}: {value}\n")
        output_file.write("\n")

    output_file.write("\n")
    output_file.write("Filebeat Results:\n")
    output_file.write("Important Events:\n")
    for event, info in filebeat_results.items():
        service_name, event_type = event
        output_file.write(f"  Service: {service_name}\n")
        output_file.write(f"      Event: {event_type}\n")
        output_file.write(f"      {info['Timestamp']}\n")
        if info['Duplicates'] > 0:
            output_file.write(f"    Previous Occurrences of this Event: {info['Duplicates']}\n")
