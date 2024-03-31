# This script was used to test how to specify the length of a query of elasticsearch.
# This script gathers 100 documents from the specified indexes to query.

import json
from datetime import datetime
from elasticsearch import Elasticsearch

# Specify Elastic Username and Password
username = 'elastic_user'
password = 'elastic_password'

# Connect to your Elasticsearch instance
es = Elasticsearch(['https://ELASTIC_IP:9200'], ca_certs='/PATH_TO_CA_CERT', basic_auth=(username, password))

# Define your query to retrieve the last 100 documents
query = {
    "query": {
        "match_all": {}
    },
    "size": 100,  # Number of documents to retrieve
    "sort": [{"@timestamp": {"order": "desc"}}]  # Sort by timestamp in descending order
}

# Specify the index or indices from which you want to retrieve data
index = "*"  # Replace with your actual index name or use "*" for all indices

# Retrieve the last 100 documents
response = es.search(index=index, body=query)

# Extract documents from the response
last_100_documents = response['hits']['hits']

# Output the retrieved documents to a file
output_file = "last_100_documents.json"
with open(output_file, "w") as f:
    json.dump(last_100_documents, f, indent=4)

print(f"Last 100 documents saved to '{output_file}'")
