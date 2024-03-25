# This is my second script to practice keyword recognition. This script parses through a system
# log file and reports open and closed sessions.

import re

# Define patterns to match session opening and closing lines
session_open_pattern = r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2}).*session opened for user (\w+)\(uid=(\d+)\) by \(uid=(\d+)\)'
session_close_pattern = r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2}).*session closed for user (\w+)'

# Open the log file
with open('testlog.txt', 'r') as file:
    # Read lines from the log file
    lines = file.readlines()
    
    # Initialize session variables
    session_user = None
    session_start_time = None
    
    # Iterate through each line in the log
    for line in lines:
        # Match session open lines
        session_open_match = re.match(session_open_pattern, line)
        if session_open_match:
            session_start_time = session_open_match.group(1)
            session_user = session_open_match.group(2)
            print(f"Session opened for user {session_user} at {session_start_time}")
        
        # Match session close lines
        session_close_match = re.match(session_close_pattern, line)
        if session_close_match:
            session_end_time = session_close_match.group(1)
            print(f"Session closed for user {session_user} at {session_end_time}")
            session_user = None
            session_start_time = None
