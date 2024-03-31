# This was an attempted script to query ALL elasticsearch documents thus far.
# It saves queries as pages, and goes until there are no documents left to query.
# Downside: This script can only reach 10000 documents before it stops.

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
    },
    "size": 1000,  # Number of documents per page
    "sort": ["_doc"]  # Sort by default field to ensure consistent order
}

# Specify the index or indices from which you want to retrieve data
index = "*"  # Replace with your actual index name or use "*" for all indices

# Initialize a list to store all retrieved documents
all_documents = []

# Retrieve the first page of results
response = es.search(index=index, body=query)

# Keep fetching pages until there are no more results
while response['hits']['hits']:
    # Extract documents from the current page of results
    hits = response['hits']['hits']
    all_documents.extend(hits)

    # Get the value of the last document from the current page
    last_document = hits[-1]
    last_sort_values = last_document['sort']

    # Update the query to fetch the next page of results using the "search after" parameter
    query['search_after'] = last_sort_values

    # Fetch the next page of results
    response = es.search(index=index, body=query)

# Output the retrieved documents to a file
output_file = "all_documents.json"
with open(output_file, "w") as f:
    json.dump(all_documents, f, indent=4)

print(f"All documents saved to '{output_file}'")
