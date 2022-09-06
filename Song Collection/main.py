from APICall import APICall
from SongDownloader import SongDownloader


def main():
    ac = APICall(["rock","metal"],100, 4)
    song_name, song_url = ac.get_song_name_url()
    sd = SongDownloader(song_name, song_url)
    sd.download_song(song_name, song_url)

if __name__ == "__main__":
    main()
