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

        # Dictionary of genres and their songs name
        self.song_list = {}
        # Dictionary of genres and their songs url
        self.song_url = {}
        
        self.song_name_dir, self.song_url_dir = self._make_song_list_url_dir()

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
        SONG_URL_LIST_PATH = os.path.join(SONG_LIST_DIR, "url_list.txt")

        return SONG_NAME_LIST_PATH, SONG_URL_LIST_PATH
    
    def _parse_song_url_from_text(self):
        """Parses song name and url from text files

        Returns:
            (dict, dict): dict of song name and url with genre as keys
        """
        song_name = {}
        song_url = {}

        with open(self.song_name_dir, "r") as f:
            text = f.read()
        genre_list = text.split("--")
        
        for genre in genre_list[:-1]:
            splitted = genre.split("\n")
            genre_name = splitted[0].replace("GENRE=", "")
            song_name[genre_name] = splitted[1:-2]   

        with open(self.song_url_dir, "r") as f:
            text = f.read()
        genre_list = text.split("--")
        
        for genre in genre_list[:-1]:
            splitted = genre.split("\n")
            genre_name = splitted[0].replace("GENRE=", "")
            song_url[genre_name] = splitted[1:-2]    


        return song_name, song_url

    def get_song_name_url(self, from_file=False):
        if from_file:
            return self._parse_song_url_from_text()
        
        song_list = self.get_song_list()
        url_list = self.get_song_url()

        self._store_song_name_url(song_list, url_list)

        return song_list, url_list
        
    def _store_song_name_url(self, song_name, song_url):

        with open(self.song_name_dir, "w") as f:
            for genre in song_name.keys():
                f.write(f"GENRE={genre}\n")
                for song in song_name[genre]:
                    f.write(f"{song}\n")
                f.write("--")

        with open(self.song_url_dir, "w") as f:
            for genre in song_url.keys():
                f.write(f"GENRE={genre}\n")
                for song in song_url[genre]:
                    f.write(f"{song}\n")
                f.write("--")


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


    def get_song_list(self):
        """Generated a dictionary of song_list with genre as key and list of song names as values

        Raises:
            ValueError: If the response doesn't send OK 200 status code

        Returns:
            dictionary: genre as key and list of song names as values
        """
        # If there is already a song list
        if self.song_list != {}:
            return self.song_list

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
        
        return self.song_list
    

    def get_song_url(self):
        """Generated a dictionary of song_list with genre as key and list of song url as values

        Raises:
            ValueError: If the response doesn't send OK 200 status code

        Returns:
            dictionary: genre as key and list of song names as values
        """

        # If song_list not generated, create it
        if self.song_list == {}:
            self.get_song_list()
        
        # If song_url already created, return it
        if self.song_url != {}:
            return self.song_url

    
        import os

        import requests
        from dotenv import load_dotenv

        # Getting youtube api key from dot env
        load_dotenv()

        # Creating a copy 
        song_list = self.song_list
        
        for genre in song_list.keys():
            song_url = []
            print(f"Getting song urls for {genre}")
            songs = song_list[genre]
            for i, song in enumerate(songs):
                env_string = f"YOUTUBE_API_KEY{i%self.num_youtube_api_keys}"
                # print(env_string)
                auth_key = os.getenv(env_string)
                if not auth_key:
                    raise ValueError("Youtube API key not found. Please add it to .env file.Use YOUTUBE_API_KEY0. Alternatively, you can use multiple keys with index starting from 0 since one API key will probably no be able to handle all requests.")


                response = requests.get(f"{self.youtube_search_base_url}?part=snippet&q={song} Lyrics&key={auth_key}")

                if response.status_code != 200:
                    print(response.json())
                    raise ValueError(f"Error fetching song names for {genre}.\nStatus code: {response.status_code}")


                # items[0] > id > videoId
                j = response.json()

                # If url accessible
                try:
                    item = j["items"][0]
                    video_id = item["id"]["videoId"]
                    video_url = f"{self.youtube_video_base_url}{video_id}"
                    song_url.append(video_url)
                # If url not accessible
                except KeyError:
                    print(f"Couldn't fetch song url of {song}")
                    songs.remove(song)
                    self.song_list[genre] = songs
                    continue
                    
                
            print(f"Got {len(song_url)} song urls for {genre}\n{'-'*50}")
            self.song_url[genre] = song_url
        return self.song_url




if __name__ == "__main__":
    import json
    ac = APICall(["rock","metal"],100, 4)
    song_name, song_url = ac.get_song_name_url()
    print(json.dumps(song_name))
    print(json.dumps(song_url))
