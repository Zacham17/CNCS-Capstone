# Query and Parsing Scripts

This directory contains the final files for querying and parsing the elasticsearch data. The description for each file is below:

**queryOneDay.py** : This file gathers the audtibeat, metricbeat, heartbeat, and filebeat data from elasticsearch that had been gathered in the past 24 hours.

**queryThreeDays.py** : This file gathers the audtibeat, metricbeat, heartbeat, and filebeat data from elasticsearch that had been gathered in the past 3 days.

**elasticParser.py** : This script reads through the gathered information from elasticsearch and then parses out only specific information and formats it in an output document to be read by the ticketing system website.
