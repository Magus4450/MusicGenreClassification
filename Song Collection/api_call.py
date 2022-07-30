import requests
import json
from dotenv import load_dotenv

import os

load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


API_URL = "https://api.jamendo.com/v3.0/tracks/"

payloads = {
    "client_id": CLIENT_ID,
    "format": "jsonpretty",
}

response = requests.get(f"{API_URL}", params=payloads)
# response = requests.get(f"https://api.jamendo.com/v3.0/tracks/?client_id={CLIENT_ID}&format=jsonpretty&limit=2&fuzzytags=groove+rock&speed=high+veryhigh&include=musicinfo&groupby=artist_id")
# print(response.text)

"""
results:
    name
    duration
    artist_name
    releasedate
    audiodownload
    shareurl
    musicinfo:
        speed
        tags:
            genres -> []

    audiodownload_allowed
"""
j = response.json()
print(j)
