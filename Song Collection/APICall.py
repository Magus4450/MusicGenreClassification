from os import system
from xml.dom import ValidationErr


class APICall:

    def __init__(self, genres, amount_each, num_youtube_api_keys=1):
        
        # Spotify API
        self.spotify_base_url = "https://api.spotify.com/v1"
        # Youtube API
        self.youtube_search_base_url = "https://www.googleapis.com/youtube/v3/search"
        # Youtube video url
        self.youtube_video_base_url = "https://www.youtube.com/watch?v="

        # Check if genres provided by user is a valid genre
        self.genres = self._validate_genres(genres)

        # Amount of songs to process
        self.amount_each = amount_each

        # Number of API Key used
        self.num_youtube_api_keys = num_youtube_api_keys

        self.song_name_dir= self._make_song_list_url_dir()

        self.song_list = {}

    def _make_song_list_url_dir(self):
        """Makes directory for song list and song url

        Returns:
            (str, str): song list directory, song url directory
        """
        import os
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        if not os.path.isdir(os.path.join(BASE_DIR, "Song List")):
            os.mkdir(BASE_DIR + "\\Song List")

        SONG_LIST_DIR = os.path.join(BASE_DIR, "Song List")

        SONG_NAME_LIST_PATH = os.path.join(SONG_LIST_DIR, "name_list.txt")

        return SONG_NAME_LIST_PATH
    
    def get_song_name_url(self):
        """Parses song name and url from text file and returns it

        Returns:
            (dict, dict): dict of song name and url with genre as keys
        """

        # Dict to store song name and url
        song_name = {}
        song_url = {}

        with open(self.song_name_dir, "r") as f:
            text = f.read()

        # Seperate into lists by genre with first item being `GENRE=<genre>`
        genre_list = text.split("----")
        if "\n" in genre_list:
            genre_list.remove("\n") # Last contains empty string

        # Last item of genre_list contains empty string
        for genre in genre_list:

            split = genre.split("\n")
            split.remove('')

            songs = split[1:]
            genre_name = split[0].split("=")[1]

            if '' in songs:
                songs.remove('')

            genre_song_list = []
            genre_songs_url = []

            for song in songs:
                if song == '':
                    continue
                name, url = song.split("->")

                genre_song_list.append(name)
                genre_songs_url.append(url)

            song_name[genre_name] = genre_song_list
            song_url[genre_name] = genre_songs_url
        
        return song_name, song_url



    def _validate_genres(self, genres):
        """Validates weather the genres provided by user is a valid genre. The list is crosschecked with genre list provided by spotify API.

        Args:
            genres (list(str)): list of genre provided by user

        Raises:
            ValueError: Raised if genre not a valid genre

        Returns:
            list(str): validated_genres
        """
        import requests

        # Generate auth token
        auth_token = self._get_spotify_access_token()
        header = {"Authorization": f"Bearer {auth_token}"}

        response = requests.get(f"{self.spotify_base_url}/recommendations/available-genre-seeds", headers=header)

        j = response.json()
        available_genres = j["genres"]
        
        for genre in genres:
            if genre not in available_genres:
                raise ValueError(f"{genre} is not a valid genre. Available genres are: {available_genres}")
        
        return genres


    def _get_spotify_access_token(self):
        """Generates access token using spotify token API using Client Id and Client Secret

        Returns:
            str: access token
        """
        import base64
        import os

        import dotenv
        import requests

        # Get client id and client secret from dot env
        dotenv.load_dotenv()
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if client_id is None or client_secret is None:
            raise ValueError("Client Id or Client Secret for Spotify not found in .env file. Use SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET as keys")

        # Auth token for Token Request
        auth_token = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode('ascii')

        # Headers for Token Request
        auth_header = {"Authorization": f"Basic {auth_token}"}
        auth_data = {"grant_type": "client_credentials"}

        # Getting Access Token
        auth_request = requests.post("https://accounts.spotify.com/api/token", headers=auth_header, data=auth_data)

        # Get the token
        auth_response = auth_request.json()
        auth_token = auth_response["access_token"]

        return auth_token

    def _store_song_name(self, song_name):
        """
        Stores song name in text file
        
        Args:
            song_name (str): song name
        """


        with open(self.song_name_dir, "w") as f:
            for genre in song_name.keys():
                f.write(f"GENRE={genre}\n")
                for song in song_name[genre]:
                    f.write(f"{song}\n")
                f.write("----\n")

    def generate_song_list(self):
        """Generates a dictionary of song names as value and genre as key by pulling values from Spotify API and stores them in a file

        Raises:
            ValueError: If the response doesn't send OK 200 status code

        Returns:
            dictionary: genre as key and list of song names as values
        """
        import datetime

        import requests
        current_year = datetime.datetime.now().year


        auth_token = self._get_spotify_access_token()
        header = {"Authorization": f"Bearer {auth_token}"}


        # Maximum amount of songs retuned at once in 50, so divide into multiple requests if more amount requested

        n_request_calls = max(1, self.amount_each // 50)

        if self.amount_each % 50 != 0:
            n_request_calls += 1

        for genre in self.genres:
            song_list = []

            print(f"Getting song names for {genre}")
            for i in range(n_request_calls):
                offset= i * 50

                response = requests.get(f"{self.spotify_base_url}/search/?q=genre:{genre}+year:2000-{current_year}&type=track&limit={min(50,self.amount_each)}&offset={offset}", headers=header)

                if response.status_code != 200:
                    raise ValueError(f"Error fetching song names for {genre}.\nStatus code: {response.status_code}")
                # Converting to json
                j = response.json()
                j = j["tracks"]

                # Adding all songs names to a list
                for item in j["items"]:
                    song_list.append(item["name"])

            # Adding the list to song_list dictionary
            self.song_list[genre] = song_list
            print(f"Got {len(song_list)} song names for {genre}\n{'-'*50}")
        
        self._store_song_name(self.song_list)
        
    

    def generate_song_url(self):
        """Generates a dictionary of song urls as value and genre as key by pulling values from Youtube API and stores them in a file

        Raises:
            ValueError: If the response doesn't send OK 200 status code

        Returns:
            dictionary: genre as key and list of song names as values
        """

        tokens_exhausted = 0
        current_token = 0
        import os

        import requests
        from dotenv import load_dotenv

        # Getting youtube api key from dot env
        load_dotenv()

    
        

        with open(self.song_name_dir, "r") as f:
            text_data = f.read()

        genre_list = text_data.split("----")
        if "\n" in genre_list:
            genre_list.remove("\n") # Last contains empty string
        with open(self.song_name_dir, 'w') as o:
            for genre in genre_list:
                split = genre.split("\n")
                if '' in split:
                    split.remove('')
                songs = split[1:]

                genre_name = split[0]
                if tokens_exhausted < self.num_youtube_api_keys:
                    print(f"Fetching URLs for {genre_name.capitalize()}")
                o.write(f"{genre_name}\n")

                length = len(songs)
                i = 0
                while i < length:
                    if tokens_exhausted == self.num_youtube_api_keys:
                        print("All youtube api keys exhausted. Please add more youtube api keys to .env file")
                        o.write(f"{songs[i]}\n")
                        tokens_exhausted +=1
                        i+=1
                        if i == len(songs):
                            o.write(f"----\n")
                        continue
                    elif tokens_exhausted > self.num_youtube_api_keys:
                        if songs[i] != '':
                            o.write(f"{songs[i]}\n")
                        i+=1
                        if i == len(songs):
                            o.write(f"----\n")
                        continue

                    if "->" in songs[i]:
                        print(f"{i:3.0f}:{len(songs):3.0f} URL already fetched for {songs[i].split('->')[0]}")
                        o.write(f"{songs[i]}\n")
                    else:
                        try:
                            env_string = f"YOUTUBE_API_KEY{current_token}"
                            auth_key = os.getenv(env_string)
                            if not auth_key:
                                raise ValidationErr("Youtube API key not found. Please add it to .env file.Use YOUTUBE_API_KEY0. Alternatively, you can use multiple keys with index starting from 0 since one API key will probably no be able to handle all requests.")
                            response = requests.get(f"{self.youtube_search_base_url}?part=snippet&q={songs[i]} Lyrics&key={auth_key}")



                            if response.status_code != 200:
                                print(f"Token {current_token} exhausted. Trying next token")
                                tokens_exhausted += 1
                                current_token += 1
                                continue


                            # items[0] > id > videoId  
                            j = response.json()
                            item = j["items"][0]
                            video_id = item["id"]["videoId"]
                            video_url = f"{self.youtube_video_base_url}{video_id}"


                            o.write(f"{songs[i]}->{video_url}\n")
                            print(f"{i:3.0f}:{len(songs):3.0f} Fetched song url of {songs[i]}")

                        except KeyError:
                            print(f"{i:3.0f}:{len(songs):3.0f} Couldn't fetch song url of {songs[i]}")
                            # o.write(f"{song}\n")
                        except ValidationErr:
                            break
                        except:
                            print(f"{i:3.0f}:{len(songs):3.0f} Couldn't fetch song url of {songs[i]}")
                            # o.write(f"{song}\n")
                    i += 1
                    if i == len(songs):
                        o.write(f"----\n")




if __name__ == "__main__":
    ac = APICall(["rock","metal", "hip-hop"],50, 1)
    song_list = ac.generate_song_list()
    song_url = ac.generate_song_url()
