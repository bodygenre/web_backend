#!/usr/bin/env python

# Description: This program takes user input for TV show searches from the blaa.ke domain and uses the Sonarr API to find the series and track newly released episodes

#Import modules
import yaml
import requests
import logging
import datetime

# Open YAML Sonarr API configuration file
with open("sonarr_tracker.yaml", "r") as settings_file:
    settings_import = yaml.safe_load(settings_file)

 
# Query Sonarr for TV_show
def queue_search(payload):
    api_endpoint = "/api/series/lookup"
    uri_endpoint = settings_import["sonarr"]["address"] + api_endpoint
    headers = {
        "content-type": "application/json",
        "X-Api-Key": settings_import["sonarr"]["api_key"]
    }
    response = requests.get(uri_endpoint, headers=headers, json=payload)
    output = response.json()
    print(output)
    return payload
	#to do - if the output length one or more use the first entry -> look this up 

