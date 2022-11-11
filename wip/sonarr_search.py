#!/usr/bin/env python3

# Description: This program takes user input for TV show searches from the blaa.ke domain and uses the Sonarr API to find the series and track newly released episodes

#Import modules
import yaml
import urllib.parse
import requests
import logging
import datetime

# Open YAML Sonarr API configuration file
with open("sonarr_tracker.yaml", "r") as settings_file:
    settings_import = yaml.safe_load(settings_file)

#Query Sonarr for TV_show
def queue_search(input):
    api_endpoint = "/api/Command"
    uri_endpoint = urlparse.urljoin(settings_import["sonarr"]["address"], api_endpoint)
    headers = {
        'content-type': 'application/json',
        'X-Api-Key': settings_import["sonarr"]["api_key"]
    }
    payload = input
    response = requests.post(uri_endpoint, headers=headers, json=payload)

    logging.debug('request submit uri %s', uri_endpoint)
    logging.debug('request submit headers %s', headers)
    logging.debug('request submit payload %s', payload)
    logging.debug('request response url: %s', response.url)
    logging.debug('request response headers: %s', response.headers)
    logging.debug('request response encoding: %s', response.apparent_encoding)
    logging.debug('request response text: %s', response.text)
    logging.debug('request response reason: %s', response.json)
    logging.info('request response reason: %s', response.reason)
    logging.info('request response status code: %s', response.status_code)
    logging.info('request response time elapsed: %s', response.elapsed)

    output = response.json()
    logging.info("Command ID = %s", output["id"])
    logging.info("Command State = %s", output["state"])


