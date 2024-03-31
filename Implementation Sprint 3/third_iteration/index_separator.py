# This script takes a file containing elasticsearch query results, and will split the metricbeat,
# auditbeat, filebeat, and heartbeat entries into seperate files.

import json

# Read the JSON file
input_file = "INPUT_FILE"
with open(input_file, "r") as f:
    documents = json.load(f)

# Initialize dictionaries to store documents for each index
metricbeat_documents = []
auditbeat_documents = []
filebeat_documents = []
heartbeat_documents = []

# Iterate through each document
for doc in documents:
    # Extract the index name from the document
    index_name = doc['_index']

    # Separate documents based on their index name
    if index_name.startswith('.ds-metricbeat-'):
        metricbeat_documents.append(doc)
    elif index_name.startswith('.ds-auditbeat-'):
        auditbeat_documents.append(doc)
    elif index_name.startswith('.ds-filebeat-'):
        filebeat_documents.append(doc)
    elif index_name.startswith('.ds-heartbeat-'):
        heartbeat_documents.append(doc)

# Output documents for each index to separate files
output_files = {
    "metricbeat_documents.json": metricbeat_documents,
    "auditbeat_documents.json": auditbeat_documents,
    "filebeat_documents.json": filebeat_documents,
    "heartbeat_documents.json": heartbeat_documents
}

for file_name, docs in output_files.items():
    with open(file_name, "w") as f:
        json.dump(docs, f, indent=4)
    print(f"{len(docs)} documents saved to '{file_name}'")
