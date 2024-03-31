# This file uses the scroll method of query, which means it check for more documents after
# a certain amount of them are queried and keeps doing this until there are no more left.
# Unfortunately, this method causes my system to timeout since there are so many documents to query.

import json
from datetime import datetime
from elasticsearch import Elasticsearch

# Specify Elastic Username and Password
username = 'elastic_user'
password = 'elastic_password'

# Connect to your Elasticsearch instance
es = Elasticsearch(['https://ELASTIC_IP:9200'], ca_certs='/PATH_TO_CA_CERT', basic_auth=(username, password))

# Define your query to retrieve all data
query = {
    "query": {
        "match_all": {}
    }
}

# Specify the index or indices from which you want to retrieve data
indices = ["*"]  # Replace with your actual index name or use "*" for all indices

# Execute the initial search query to get the first page of results
scroll_results = es.search(index=indices, body=query, scroll='1m', size=1000)

# Initialize a list to store all retrieved documents
all_documents = []

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
output_file = "all_documents.json"
with open(output_file, "w") as f:
    json.dump(all_documents, f, indent=4)

print(f"All documents saved to '{output_file}'")
