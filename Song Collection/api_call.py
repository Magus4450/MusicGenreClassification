from email import header
import requests
import json
from dotenv import load_dotenv

import os

load_dotenv()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


API_URL = "https://api.jamendo.com/v3.0/tracks/"
spot = "https://api.spotify.com/v1/search"
auth_header = {"Authorization": "Basic {}".format("OTVlNjJlOTc3ODU0NDBmODhmZGFjMjQwMjAxZmFkYjQ6ZjcwZTdhYjFkYmI2NDcyMThjMjhhNWZkNzU1MGQ4MWQ=")}
auth_data = {"grant_type": "client_credentials"}
print(auth_header)
print(auth_data)
auth_request = requests.post("https://accounts.spotify.com/api/token", headers=auth_header, data=auth_data)
auth_response = auth_request.json()
auth_token = auth_response["access_token"]
payloads = {
    "client_id": CLIENT_ID,
    "format": "json",
    "tags": "rock",
    "boost": "popularity_total",
    "audiodlformat": "mp32",

}

you = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=2&q=I Aint Worried Lyrics&key=AIzaSyChgskfyEgxrkTFdLlwof_O24uM644vSb8"


header = {"Authorization": "Bearer {}".format(auth_token)}
# response = requests.get(f"{spot}/?q=genre:rock+year:2000-2022&type=track&limit=2", headers=header)


response = requests.get(you)

# response = requests.get(f"{API_URL}", params=payloads)


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
# j = json.decoder.JSONDecod
# er()
# j = response.json()
# j = j["tracks"]
# for k in j["items"]:
#     print(k["name"])
# j = j["items"]
# print(j[0]["name"])
formatted_string = json.dumps(response.json(), indent=4)
print(formatted_string)
# parsed = json.loads(response.json())

# print(json.dumps(parsed, indent=2, sort_keys=True))