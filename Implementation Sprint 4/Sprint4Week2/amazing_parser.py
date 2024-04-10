import json

# Function to parse data from Auditbeat index
def parse_auditbeat(data):
    host_info = {}

    # Default Linux users associated with services
    default_users = ["root", "systemd", "auditd"]

    for item in data:
        if "_source" in item:
            source = item["_source"]
            host_name = source.get("host", {}).get("name", "")
            user_name = source.get("user", {}).get("name", "")
            process_name = source.get("process", {}).get("name", "")
            action = source.get("event", {}).get("action", "")

            if host_name:
                if host_name not in host_info:
                    host_info[host_name] = {"Users": set(), "Process Stops": {}, "Process Starts": {}}
                # Exclude default Linux users associated with services
                if user_name and user_name not in default_users:
                    host_info[host_name]["Users"].add(user_name)
                if action == "stopped":
                    timestamp = source.get("@timestamp", "")
                    host_info[host_name]["Process Stops"].setdefault(process_name, []).append(timestamp)
                elif action == "started":
                    timestamp = source.get("@timestamp", "")
                    host_info[host_name]["Process Starts"].setdefault(process_name, []).append(timestamp)

    return host_info

# Function to parse data from Heartbeat index
def parse_heartbeat(data):
    failed_connections = 0
    down_services = {}
    most_recent_failed_connection = None
    most_recent_down_service = None

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
            elif status == "failure":
                failed_connections += 1
                if not most_recent_failed_connection or timestamp > most_recent_failed_connection:
                    most_recent_failed_connection = timestamp

    return failed_connections, down_services, most_recent_failed_connection, most_recent_down_service

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
                    "Memory Usage": source.get("system", {}).get("memory", {}).get("usage", {}).get("bytes", ""),
                    "CPU Utilization": source.get("system", {}).get("cpu", {}).get("total", {}).get("pct", ""),
                    "Inbound Traffic": source.get("system", {}).get("network", {}).get("in", {}).get("bytes", ""),
                    "Disk Usage": source.get("system", {}).get("filesystem", {}).get("usage", {}).get("bytes", "")
                }

    return monitored_hosts

# Function to parse data from Filebeat index
def parse_filebeat(data):
    important_events = []
    process_count = {}

    total_logs = len(data)

    for item in data:
        if "_source" in item:
            source = item["_source"]
            process_name = source.get("process", {}).get("name", "")
            if process_name:
                process_count[process_name] = process_count.get(process_name, 0) + 1

            timestamp = source.get("@timestamp", "")
            message = source.get("message", "")
            process = source.get("process", {})
            if process.get("name") == "systemd" and "Stopped" in message:
                service_name = message.split("Stopped ")[1].strip(".")
                important_events.append({"Service": service_name, "Event": "Stopped", "Timestamp": timestamp})
            # Add more conditions for other important events here

    process_percentage = {process: (count / total_logs) * 100 for process, count in process_count.items()}

    return important_events, process_percentage

# Read data from the JSON file
with open("documents_past_7_days.json", "r") as file:
    data = json.load(file)

# Parsing data from each index
auditbeat_data = [doc for doc in data if doc["_index"].startswith(".ds-auditbeat")]
heartbeat_data = [doc for doc in data if doc["_index"].startswith(".ds-heartbeat")]
metricbeat_data = [doc for doc in data if doc["_index"].startswith(".ds-metricbeat")]
filebeat_data = [doc for doc in data if doc["_index"].startswith(".ds-filebeat")]

auditbeat_results = parse_auditbeat(auditbeat_data)
heartbeat_results = parse_heartbeat(heartbeat_data)
metricbeat_results = parse_metricbeat(metricbeat_data)
filebeat_results = parse_filebeat(filebeat_data)

# Output the results
print("\033[92mAuditbeat Results:\033[0m")
for host, info in auditbeat_results.items():
    print(f"Host: {host}")
    print(f"  Users: {', '.join(info['Users'])}")
    print("  Process Stops:")
    for process, timestamps in info['Process Stops'].items():
        for timestamp in timestamps:
            print(f"    {process} stopped at {timestamp}")
    print("  Process Starts:")
    for process, timestamps in info['Process Starts'].items():
        for timestamp in timestamps:
            print(f"    {process} started at {timestamp}")

failed_connections_count, down_services_count, most_recent_failed_connection, most_recent_down_service = heartbeat_results

print("\n")
print("\033[92mHeartbeat Results:\033[0m")
print("\033[94mFailed Connections:\033[0m", failed_connections_count)
print("\033[94mDown Services:\033[0m", len(down_services_count))
print("\033[94mList of Down Services:\033[0m")
for service, timestamp in down_services_count.items():
    print(f"  {service}: Found down at {timestamp}")

print("\n")
print("\033[92mMetricbeat Results:\033[0m")
monitored_hosts = metricbeat_results
print("\033[94mHosts being Monitored:\033[0m")
for host, details in monitored_hosts.items():
    print(f"  {host}")
    for metric, value in details.items():
        print(f"    {metric}: {value}")

print("\n")
print("\033[92mFilebeat Results:\033[0m")
print("\033[94mImportant Events:\033[0m")
for event in filebeat_results[0]:
    print(f"  Service: {event['Service']}, Event: {event['Event']}, Timestamp: {event['Timestamp']}")
print("\nProcess Log Percentage:")
for process, percentage in filebeat_results[1].items():
    print(f"  {process}: {percentage:.2f}%")
