from APICall import APICall
from SongDownloader import SongDownloader


def main():
    ac = APICall(["blues","classical", "country", "disco", "hip-hop", "jazz", "metal", "pop", "reggae", "rock"],500, 13)
    # ac.get_song_list()
    # ac.generate_song_url()
    song_name ,song_url = ac.get_song_name_url()
    print(song_name.keys())
    for key in song_name.keys():
        print(len(song_name[key]), len(song_url[key]))

    print(song_url["rock"])
    # sd = SongDownloader()
    # sd.download_song(song_name, song_url)

if __name__ == "__main__":
    main()
