from FeatureExtraction.FeatureExtractor import FeatureExtractor
from SongCollection.APICall import APICall
from SongCollection.SongDownloader import SongDownloader


def main():
    # Making APICall object to acquire song name and url of 50 songs of 2 genre each using 1 API key.
    ac = APICall(["classical", "rock"],50, 1)

    # Getting song names
    ac.generate_song_list()

    # Getting song URLs
    ac.generate_song_url()

    # Fetching the name and url stored in the file
    song_name ,song_url = ac.get_song_name_url()

   
    for key in song_name.keys():
        print(f'Genre: {key} Songs: {len(song_name[key])} URLs: {len(song_url[key])}')

    # Initializing SongDownloader object to download and segment songs using 10 threads
    sd = SongDownloader(10)
    
    # Downloading and Segmenting songs
    sd.download_song(song_name, song_url)


    import warnings

    # Ignoring warning thrown by Librosa because of mp3 format
    warnings.filterwarnings("ignore")

    # Initializing object for FeatureExtractor using 10 threads
    fe = FeatureExtractor(n_threads=10)

    # Extracting Features -> stored into data.csv
    fe.extract_features()


if __name__ == "__main__":
    main()
