# This file is a third parser that I made to analyze elasticsearch queries. This script
# looks for events where services are down or connections are unsuccessful and returns the event details.

import json

# Load the retrieved documents from the file
with open("INPUT_FILE_GOES_HERE", "r") as f:
    documents = json.load(f)

# Initialize lists to store important events
service_stops = []
connection_failures = []

# Iterate through each document
for doc in documents:
    # Check if the document contains a service stop event
    if doc.get("_source", {}).get("event", {}).get("action") == "service_stop":
        service_stops.append(doc)

    # Check if the document contains a connection failure event
    if doc.get("_source", {}).get("event", {}).get("action") == "connection_failure":
        connection_failures.append(doc)

# Output the important events
print("Service Stop Events:")
for event in service_stops:
    print(json.dumps(event, indent=4))

print("\nConnection Failure Events:")
for event in connection_failures:
    print(json.dumps(event, indent=4))
