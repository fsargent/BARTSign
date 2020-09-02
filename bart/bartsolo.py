from pprint import pformat
from dotenv import load_dotenv
import os
import time
import requests
import json
import logging
import inflect
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(format='%(asctime)s %(message)s', level=LOGLEVEL)
p = inflect.engine()

load_dotenv()

API_KEY = os.getenv("API_KEY")

# Inspiration and resources:
# https://uxdesign.cc/countdown-clocks-for-the-mta-79fa8013a0e7
# http://api.bart.gov/docs/etd/etd.aspx

bartURL = f'http://api.bart.gov/api/etd.aspx?cmd=etd&orig={self.args.station}&json=y&key={API_KEY}'
if self.args.platform:
    bartURL = f'http://api.bart.gov/api/etd.aspx?cmd=etd&orig={self.args.station}&json=y&plat={self.args.platform}&key={API_KEY}'
bart_response = requests.get(bartURL)
logging.debug(pformat(bart_response.text))
logging.debug(pformat(bart_response.text))
if bart_response.status_code != 200:
    raise Exception("Couldn't connect to BART.",
                    str(bart_response.status_code))
if "xml" in bart_response.headers['content-type']:
    raise Exception(bart_response.text.split("details")[1], "400")
schedule = json.loads(bart_response.text)
if hasattr("warning", schedule["root"]["message"]):
    raise Exception(schedule["root"]["message"]["warning"], "400")
trains = []

# Turn the format into an array of trains
destinations = schedule["root"]["station"][0]["etd"]
for destination in destinations:
    for train in destination["estimate"]:
        train["destination"] = destination["destination"]
        if train["minutes"] == "Leaving":
            train["minutes"] = "0"
        train["minutes"] = train["minutes"]

        trains.append(train)

trains = sorted(trains, key=lambda i: int(i['minutes']))

logging.info(pformat(trains))

if trains[0]["minutes"] == "0":
    trains[0]["minutes"] = "Now"

print(trains)
