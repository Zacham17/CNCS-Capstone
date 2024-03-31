# This file reads a file containing metricbeat, auditbeat, filebeat, and heartbeat elasticsearch
# query results, and outputs how many down services, and failed connections are recorded, as well
# as the names of any services that were reported as down.

import json

# Function to parse data from Auditbeat index
def parse_auditbeat(data):
    failed_connections = 0
    down_services = 0
    most_recent_failed_connection = None
    most_recent_down_service = None
    down_service_names = set()

    for item in data:
        if "_source" in item:
            source = item["_source"]
            timestamp = source.get("@timestamp", "")
            event = source.get("event", {})
            if "action" in event and event["action"] == "failure":
                failed_connections += 1
                if not most_recent_failed_connection or timestamp > most_recent_failed_connection:
                    most_recent_failed_connection = timestamp
            elif "outcome" in event and event["outcome"] == "failure":
                down_services += 1
                if not most_recent_down_service or timestamp > most_recent_down_service:
                    most_recent_down_service = timestamp
                service_name = source.get("service", {}).get("name", "")
                if service_name:
                    down_service_names.add(service_name)

    return failed_connections, down_services, most_recent_failed_connection, most_recent_down_service, down_service_names

# Function to parse data from Heartbeat index
def parse_heartbeat(data):
    failed_connections = 0
    down_services = 0
    most_recent_failed_connection = None
    most_recent_down_service = None
    down_service_names = set()

    for item in data:
        if "_source" in item:
            source = item["_source"]
            timestamp = source.get("@timestamp", "")
            summary = source.get("summary", {})
            status = summary.get("status", "")
            if status == "down":
                down_services += 1
                if not most_recent_down_service or timestamp > most_recent_down_service:
                    most_recent_down_service = timestamp
                monitor_name = source.get("monitor", {}).get("name", "")
                if monitor_name:
                    down_service_names.add(monitor_name)
            elif status == "failure":
                failed_connections += 1
                if not most_recent_failed_connection or timestamp > most_recent_failed_connection:
                    most_recent_failed_connection = timestamp

    return failed_connections, down_services, most_recent_failed_connection, most_recent_down_service, down_service_names

# Function to parse data from Metricbeat index
def parse_metricbeat(data):
    failed_connections = 0
    down_services = 0
    most_recent_failed_connection = None
    most_recent_down_service = None
    down_service_names = set()

    for item in data:
        # Add your parsing logic for Metricbeat data here
        pass

    return failed_connections, down_services, most_recent_failed_connection, most_recent_down_service, down_service_names

# Function to parse data from Filebeat index
def parse_filebeat(data):
    failed_connections = 0
    down_services = 0
    most_recent_failed_connection = None
    most_recent_down_service = None
    down_service_names = set()

    for item in data:
        # Add your parsing logic for Filebeat data here
        pass

    return failed_connections, down_services, most_recent_failed_connection, most_recent_down_service, down_service_names

# Read data from the JSON file
with open("INPUT_FILE_GOES_HERE", "r") as file:
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

# Displaying parsed data
print("Auditbeat Results:")
print("Failed Connections:", auditbeat_results[0])
print("Down Services:", auditbeat_results[1])
print("Most Recent Failed Connection Timestamp:", auditbeat_results[2])
print("Most Recent Down Service Timestamp:", auditbeat_results[3])
print("Down Service Names:", auditbeat_results[4])

print("\nHeartbeat Results:")
print("Failed Connections:", heartbeat_results[0])
print("Down Services:", heartbeat_results[1])
print("Most Recent Failed Connection Timestamp:", heartbeat_results[2])
print("Most Recent Down Service Timestamp:", heartbeat_results[3])
print("Down Service Names:", heartbeat_results[4])

print("\nMetricbeat Results:")
print("Failed Connections:", metricbeat_results[0])
print("Down Services:", metricbeat_results[1])
print("Most Recent Failed Connection Timestamp:", metricbeat_results[2])
print("Most Recent Down Service Timestamp:", metricbeat_results[3])
print("Down Service Names:", metricbeat_results[4])

print("\nFilebeat Results:")
print("Failed Connections:", filebeat_results[0])
print("Down Services:", filebeat_results[1])
print("Most Recent Failed Connection Timestamp:", filebeat_results[2])
print("Most Recent Down Service Timestamp:", filebeat_results[3])
print("Down Service Names:", filebeat_results[4])
