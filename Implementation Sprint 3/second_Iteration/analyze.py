# This script is my first attempt at analyzing the contents of an elasticsearch query.
# This script reads through an input file and returns the number of unsuccessful and successful
# connections found

import json

# Define variables to count successful and failed connections
successful_connections = 0
failed_connections = 0

# Specify the path to the output file
input_file = 'INPUT_FILE_ NAME
# Open the output file for reading
with open(input_file, 'r') as f:
    # Read lines from the file
    lines = f.readlines()

    # Iterate through each line
    for line in lines:
        # Check if the line starts with '#', indicating a timestamp line
        if line.startswith('#'):
            # Skip timestamp lines
            continue

        # Try parsing JSON data from the line
        try:
            event_data = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from line: {line.strip()}")
            print(f"JSONDecodeError: {e}")
            continue

        # Check for indicators of successful or failed connection
        if 'result' in event_data and event_data['result'] == 'success':
            successful_connections += 1
        elif 'result' in event_data and event_data['result'] == 'failure':
            failed_connections += 1

# Print the analysis results
print("Analysis of Connection Events:")
print(f"Successful Connections: {successful_connections}")
print(f"Failed Connections: {failed_connections}")
