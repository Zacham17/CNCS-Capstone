import json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

# Specify Elastic Username and Password
username = 'elastic_user'
password = 'elastic_password'

# Connect to your Elasticsearch instance
es = Elasticsearch(['https://192.168.229.137:9200'], ca_certs='./ca.crt', basic_auth=(username, password))

# Calculate the start and end dates for the past day
end_date = datetime.now()
start_date = end_date - timedelta(days=1)

# Format dates in Elasticsearch format (ISO 8601)
start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

# Define your query to retrieve documents for the past day
query = {
    "query": {
        "range": {
            "@timestamp": {
                "gte": start_date_str,
                "lte": end_date_str
            }
        }
    },
    "size": 1000  # Number of documents to retrieve per page
}

# Specify the index or indices from which you want to retrieve data
index = "*"  # Replace with your actual index name or use "*" for all indices

# Initialize a list to store all retrieved documents
all_documents = []

# Execute the initial search query to get the first page of results
scroll_results = es.search(index=index, body=query, scroll='1m')

# Continue retrieving pages until all documents are fetched
while True:
    # Extract documents from the current page of results
    hits = scroll_results['hits']['hits']
    all_documents.extend(hits)

    # Check if there are more results to fetch
    if len(hits) < 1000:
        break

    # Get the scroll ID for the next page of results
    scroll_id = scroll_results['_scroll_id']

    # Retrieve the next page of results using the scroll ID
    scroll_results = es.scroll(scroll_id=scroll_id, scroll='1m')

# Output the retrieved documents to a file
output_file = "queryData.json"
with open(output_file, "w") as f:
    json.dump(all_documents, f, indent=4)

print(f"All documents for the past 24 hours saved to '{output_file}'")
