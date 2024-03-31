# This script only queries for documents in elasticsearch from the past 7 days. The downside of this 
# script is that is can only query for 10000 entries before stopping. The allTimeSearch.py file
# resolves this issue though.

import json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

# Specify Elastic Username and Password
username = 'elastic_user'
password = 'elastic_password'

# Connect to your Elasticsearch instance
es = Elasticsearch(['https://ELASTIC_IP:9200'], ca_certs='/PATH_TO_CA_CERT', basic_auth=(username, password))

# Calculate the start and end dates for the past 7 days
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Format dates in Elasticsearch format (ISO 8601)
start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

# Define your query to retrieve documents for the past 7 days
query = {
    "query": {
        "range": {
            "@timestamp": {
                "gte": start_date_str,
                "lte": end_date_str
            }
        }
    },
    "size": 10000  # Number of documents to retrieve
}

# Specify the index or indices from which you want to retrieve data
index = ["auditbeat-*","heartbeat-*","metricbeat-*","filebeat-*"]  # Replace with your actual index name or use "*" for all indices

# Retrieve documents for the past 7 days
response = es.search(index=index, body=query)

# Extract documents from the response
documents_past_7_days = response['hits']['hits']

# Output the retrieved documents to a file
output_file = "documents_week.json"
with open(output_file, "w") as f:
    json.dump(documents_past_7_days, f, indent=4)

print(f"Documents for the past 7 days saved to '{output_file}'")
