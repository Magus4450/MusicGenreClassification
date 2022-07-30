

class SongDownloader:
    def __init__(self):
        
        self.SEGMENT_DURATION = 10 # Seconds
        self.root_path, self.song_dir_path = self._make_song_dir()

    def _make_song_dir(self):
        """Private method to create directory to store downloaded songs in, if not already created

        Returns:
            Tuple(str, str): Root path of the project and path of songs folder
        """
        import os
        # Project Path
        root_path = os.path.dirname(os.path.realpath(__file__))

        # If Song folder not made, make it
        if not os.path.isdir(os.path.join(root_path, "songs")):
            os.mkdir(root_path + "\\songs")

        # Get Path of songs folder
        songs_folder = os.path.join(root_path, "songs")

        return root_path, songs_folder

    def download_song(self, url, filename, duration, genres):
        """Downloads song from the given url and stores it in songs folder. Calls private method _segment_song


        Args:
            url (str): url of song download
            filename (str): base name of the song
            duration (int): duration of the song
            genres (list): genres of song
        """
        if ".mp3" not in filename:
            filename += ".mp3"

        import urllib.request
        song_path = f"{self.song_dir_path}\\{filename}"
        
        # Download the song from url and store it on song_path
        urllib.request.urlretrieve(url, song_path)

        # Segment the song
        self._segment_song(song_path, filename, duration, genres)


    def _segment_song(self, song_path, filename, duration, genres):
        
        # Diving song into n_segments of SEGENMENT_DURATION seconds
        n_segments = (duration // self.SEGMENT_DURATION)
        remainder = duration % self.SEGMENT_DURATION

        if remainder != 0:
            n_segments += 1


        import pydub
        import os

        # FFMPEG required for audio files other than .wav
        ffmpeg_path = os.path.join(self.root_path, 'FFMPEG')
        pydub.AudioSegment.converter = os.path.join(ffmpeg_path, 'ffmpeg.exe')                 
        pydub.AudioSegment.ffprobe = os.path.join(ffmpeg_path, 'ffprobe.exe')    

        song = pydub.AudioSegment.from_mp3(song_path)


        print(n_segments)
        for s in range(n_segments):

            # In milliseconds
            t1 = s * 1000
            t2 = min(t1 + 10000, duration*1000)
        
            new_file_name = f"{'_'.join(genres)}_{s+1}_{filename}"
            
            segment = song[t1:t2]
            segment.export(os.path.join(self.song_dir_path,new_file_name), format="mp3") 



if __name__ == "__main__":
    url = "https://prod-1.storage.jamendo.com/download/track/1532771/mp32/"
    song_name = "Let Me Hear You I"
    duration = 54
    genres = ["funk","pop"]
    sd = SongDownloader()
    sd.download_song(url, song_name, duration, genres)

# from pydub import AudioSegment
# t1 = t1 * 1000 #Works in milliseconds
# t2 = t2 * 1000
# newAudio = AudioSegment.from_wav("oldSong.wav")
# newAudio = newAudio[t1:t2]
# newAudio.export('newSong.wav', format="wav") 

    