# Music Genre Classification
This is a repository for Music Genre Classification Project which includes Data Collection, Feature Extraction, Training and Deployment.

## **Virtual Environment**

With virtual environment, you can easily install all requirements in one go. To do so, follow these steps:

1. Create a virtual environment <br> ```python -m venv env``` 
2. Activate the virtual environment <br> **Windows:** ```./env/Scripts/activate``` <br> **Linux:** ```source env/bin/actiavte``` 
3. Install requirements <br> ```pip install -r requirements.txt```



## **1. Data Collection**

Data in collected in a four step process.

1. Song names fetched from Spotify API according to provided Genres.
2. Youtube video URL fetched from Youtube API from the song names.
3. Songs downloaded using those Youtube video URLs.
4. Songs segmented into clips of specified seconds.

**How to use**
1. Install required libraries
    - [FFMPEG](https://ffmpeg.org/) (*Add to path*)
    - [PyTube](https://pytube.io/en/latest/)
    - [PythonDotEnv](https://pypi.org/project/python-dotenv/)
    - [Requests](https://pypi.org/project/requests/)
2. Acquire required API Keys (*Store all acquired Keys in SongCollection/.env*)
    1. Spotify API Keys
        - Login to [SpotifyDev](https://developer.spotify.com/dashboard)
        - Store keys as follows in .env file
            - ```SPOTIFY_CLIENT_ID = Your client id```
            - ```SPOTIFY_CLIENT_SECRET = Your client secret```
    2. Youtube API Keys
        - Login to [GoogleCloudConsole](https://console.cloud.google.com/)
        - Make a Project
        - Enable [YouTubeAPI](https://console.cloud.google.com/apis/api/youtube.googleapis.com)
        - In sidetabs, go to Credentials > Create API Key
        - Store keys as follows in .env file (*You can use more than one. One key can be used to get URls of about 500 songs*)
            - ```YOUTUBE_API_KEY0 = Your 1st api key```
            - ```YOUTUBE_API_KEY1 = Your 2nd api key```
            - ```. . . ```
3. Run the program
    1. For Song name and URL
        1. Make object of APICall as<br> ```ac = APICall(genre_list, number_of_songs, number_of_youtube_keys)``` <br> Example: <br> ```ac = APICall(["classical", "rock"],50, 1)```
        2. Get song names <br> ```ac.generate_song_list()```
        3. Get song URLs <br> ```ac.generate_song_url()```
        4. Access song name and urls from text files <br> ```song_name ,song_url = ac.get_song_name_url()```

    2. To Download and Segment
        1. Make object of SongDownloader as <br> ```sc = SongDownloader(n_threads, segment_duration)``` <br> Example: <br> ```sd = SongDownloader(10, 30)```
        2. Download and segment <br> ```sd.download_song(song_name, song_url)```

---

## **2. Feature Extraction**

Feature Extraction makes use of Librosa to extract a total of 38 features from both frequenct domain and time domain.
Extracted features are Mean and Standard Deviations of:
- Amplitude Envelope
- Root Mean Squared Energy
- Zero Crossing Rate
- Band Energy Ratio
- Spectral Centroid
- Bandwidth
- 13 Mel Frequency Cepstral Coefficients (MFCCs)

**How to use**
1. Complete *How to use* of **Data Collection**
2. Install required libraries
    - [FFMPEG](https://ffmpeg.org/) (*Add to path*)
    - [Librosa](https://librosa.org/doc/latest/index.html)
    - [Numpy](https://numpy.org/)
    - [Pandas](https://pandas.pydata.org/)
3. Run the program
    1. Make object of FeatureExtractor as <br> ```fe = FeatureExtractor(segment_duration, n_threads)``` (*Segment duration must be same as **Data Collection***) <br> Example: <br> ```fe = FeatureExtractor(30, 10)```
    2. Extract features <br> ```fe.extract_features()```

---
## **3. Training**

In this part, I have dome some preliminary exploratory data analysis along with visualization of different features that has been extracted .

The data was trained on different models with primary evalulation metrics being the F1 Score and Confusion Matrix. The data being highly imbalanced, balancing techniques like UnderSampling and OverSampling were used. Random Search was also employed to find best hyperparameters for the model.

The best model was a RandomForestClassifer with test F1 Score of 70%. This model was trained by dropping BER_Mean and BER_Std columns as these data had multiple discrepancies. 

The model was extracted into a file by pickle to be used in deployment.

---
## **4. Deployment**

*In Progress*

---
