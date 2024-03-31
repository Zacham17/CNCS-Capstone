# This file is used to query data from elasticsearch. This script queries from all indexes.
# The data gathered is output into a file

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

# Execute the search query
results = es.search(index=indices, body=query)


# Extract the _source field from each hit and store it in a list
hits_sources = [hit['_source'] for hit in results['hits']['hits']]

# Output the search results to a file
output_file = "search_results.json"
with open(output_file, "w") as f:
    json.dump(hits_sources, f, indent=4)

print(f"Search results saved to '{output_file}'")
