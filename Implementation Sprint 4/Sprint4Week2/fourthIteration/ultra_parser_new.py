import json
from collections import defaultdict
from datetime import datetime, timedelta

# Function to convert bytes to megabytes
def bytes_to_megabytes(bytes_value):
    return f"{round(float(bytes_value) / (1024 * 1024), 2)} MB"

# Function to convert CPU utilization to percentage
def convert_to_percentage(value):
    return f"{round(float(value) * 100, 2)}%"

# Function to convert bytes to data transfer rate
def bytes_to_data_transfer_rate(bytes_value):
    return f"{round(float(bytes_value) / (1024 * 1024), 2)} MB/s"

# Function to convert milliseconds to seconds
def ms_to_seconds(ms_value):
    return f"{round(ms_value / 1000, 2)} s"

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
        up_timestamp = datetime.fromisoformat(info["Timestamp"].replace("Z", "+00:00"))
        started_at = datetime.fromisoformat(info["Started At"].replace("Z", "+00:00"))
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
            if host not in monitored_hosts:
                monitored_hosts[host] = {
                    "Memory Usage": bytes_to_megabytes(source.get("system", {}).get("process", {}).get("memory", {}).get("rss", {}).get("bytes", "")),
                    "CPU Utilization": convert_to_percentage(float(source.get("system", {}).get("process", {}).get("cpu", {}).get("total", {}).get("pct", 0))),
                    "Inbound Network Traffic": bytes_to_data_transfer_rate(float(source.get("system", {}).get("process", {}).get("io", {}).get("read_bytes", 0))),
                    "Outbound Network Traffic": bytes_to_data_transfer_rate(float(source.get("system", {}).get("process", {}).get("io", {}).get("write_bytes", 0))),
                    "Disk read": bytes_to_data_transfer_rate(float(source.get("system", {}).get("process", {}).get("io", {}).get("read_bytes", 0))),
                    "Disk write": bytes_to_data_transfer_rate(float(source.get("system", {}).get("process", {}).get("io", {}).get("write_bytes", 0)))
                }

                # Calculate Disk Utilization
                disk_utilization = source.get("system", {}).get("filesystem", {}).get("used", {}).get("pct", 0)
                monitored_hosts[host]["Disk Utilization"] = f"{round(disk_utilization * 100, 2)}%"

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
with open("documents_past_7_days.json", "r") as file:
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
    output_file.write("\033[92mAuditbeat Results:\033[0m\n")
    for host, details in auditbeat_results.items():
        output_file.write(f"\033[94mHost: {host}\033[0m\n")
        output_file.write(f"  Users: {', '.join(details['Users'])}\n")
        output_file.write(f"  Unique Processes: {details['Unique Processes']}\n")
        output_file.write(f"  OS Distribution: {details['OS Distribution']}\n")
        output_file.write(f"  Uptime: {details['Uptime']}\n")

    output_file.write("\n")
    output_file.write("\033[92mHeartbeat Results:\033[0m\n")
    output_file.write("\033[94mDown Services:\033[0m " + str(len(down_services_count)) + "\n")
    output_file.write("\033[94mList of Down Services:\033[0m\n")
    for service, timestamp in down_services_count.items():
        output_file.write(f"  {service}: Found down at {timestamp}\n")
    output_file.write("\033[94mUp Services:\033[0m " + str(len(up_services)) + "\n")
    output_file.write("\033[94mList of Up Services and Duration:\033[0m\n")
    for service, info in up_services.items():
        output_file.write(f"  {service}: Up since {info['Timestamp']} (Duration: {info['Duration']})\n")

    output_file.write("\n")
    output_file.write("\033[92mMetricbeat Results:\033[0m\n")
    monitored_hosts = metricbeat_results
    output_file.write("\033[94mHosts being Monitored:\033[0m\n")
    for host, details in monitored_hosts.items():
        output_file.write(f"\nHostname: {host}\n")
        for metric, value in details.items():
            output_file.write(f"    {metric}: {value}\n")

    output_file.write("\n")
    output_file.write("\033[92mFilebeat Results:\033[0m\n")
    output_file.write("\033[94mImportant Events:\033[0m\n")
    for event, info in filebeat_results.items():
        service_name, event_type = event
        output_file.write(f"  Service: {service_name}\n")
        output_file.write(f"      Event: {event_type}\n")
        output_file.write(f"      {info['Timestamp']}\n")
        if info['Duplicates'] > 0:
            output_file.write(f"    Previous Occurrences of this Event: {info['Duplicates']}\n")
