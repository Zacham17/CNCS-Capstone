# This file is my second attempt at a script to parse through an elasticsearch query.
# This script looks at specific values in each document queried to determine unsusccessful connections
# and then returns the details of the unsuccessful connection(such as timestamp)

import json

# Read the JSON file containing the search results
file_path = "INPUT_FILE"

with open(file_path, "r") as file:
    search_results = json.load(file)

# Initialize counters for successful and unsuccessful connections
successful_connections = 0
unsuccessful_connections = 0

# Lists to store details of unsuccessful connections
unsuccessful_details = []

# Iterate through each entry in the search results
for entry in search_results:
    # Check if the "flow" field exists in the entry
    if "flow" in entry:
        # If the "flow" field is present and "complete" is True, it's a successful connection
        if entry["flow"].get("complete"):
            successful_connections += 1
        # If the "flow" field is present but "complete" is False, it's an unsuccessful connection
        else:
            unsuccessful_connections += 1
            # Extract and store details of unsuccessful connections
            timestamp = entry["@timestamp"]
            destination_ip = entry["destination"]["ip"]
            hostname = entry["host"]["name"]
            unsuccessful_details.append({"timestamp": timestamp, "destination_ip": destination_ip, "hostname": hostname})

# Print the counts of successful and unsuccessful connections
print("Successful connections:", successful_connections)
print("Unsuccessful connections:", unsuccessful_connections)

# Print details of unsuccessful connections
if unsuccessful_connections > 0:
    print("\nDetails of unsuccessful connections:")
    for detail in unsuccessful_details:
        print("Timestamp:", detail["timestamp"])
        print("Destination IP:", detail["destination_ip"])
        print("Hostname:", detail["hostname"])
        print()
