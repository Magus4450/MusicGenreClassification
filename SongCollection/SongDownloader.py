
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

from pytube import YouTube

from ..ProgressBar.progressBar import printProgressBar


class SongDownloader:
    def __init__(self, n_threads, segment_duration=30):
        """

        Args:
            n_threads (int): Number of threads to utilize for downloading and segmenting songs
            segment_duration (int, optional): Duration in seconds to segment song into. Defaults to 30.
        """
        # Number of threads ot utlilize to download and segment songs
        self.n_threads = n_threads

        # Duration for each segmented clip
        self.SEGMENT_DURATION = segment_duration # Seconds

        # Get root path of the project and initialize song directory
        self.original_folder, self.segment_folder = self._make_song_dir()

        # To keep track of progress
        self.completed_songs = 0
        self.total_songs = 0

    def _make_song_dir(self):
        """Private method to create directory to store downloaded songs in, if not already created

        Returns:
            Tuple(str, str): Root path of the project and path of songs folder
        """

        # Project Path
        root_path = os.path.dirname(os.path.realpath(__file__))

        # If Song folder not made, make it
        if not os.path.isdir(os.path.join(root_path, "songs")):
            os.mkdir(root_path + "\\songs")

        root_path = os.path.join(root_path, "songs")

        orignal_folder = os.path.join(root_path, "original")
        
        if not os.path.isdir(orignal_folder):
            os.mkdir(root_path + "\\original")
        


        # Get Path of songs segment folder
        segment_folder_name = f"segment_{self.SEGMENT_DURATION}"

        segment_folder = os.path.join(root_path, segment_folder_name)

        # If Song folder not made, make it
        if not os.path.isdir(segment_folder):
            os.mkdir(root_path + f"\\{segment_folder_name}")



        return orignal_folder, segment_folder

    def _download_individual_song(self, genre, song_name, song_url):
        """Private method to download and segment one song at a time

        Args:
            genre (str): Genre of song
            song_name (str): Name of song
            song_url (str): Youtube URL of song
        """


        # Path of the song where it is going to be downloaded
        downloaded_file_path = self.original_folder + "\\" + song_name.strip('?!@#$%^&*():;') + ".mp3"

        # Path of first segment of the song
        segmented_file_name = f'{genre}_00_{song_name}.mp3'
        segmented_file_path = os.path.join(self.segment_folder, segmented_file_name)

        # If song is not already downloaded
        if not (os.path.isfile(downloaded_file_path)):

            yt = YouTube(song_url)

            # Get the audio stream
            audio = yt.streams.filter(only_audio=True).first()
            output_file = audio.download(output_path=self.original_folder)

            # Absolute path of downloaded song
            base, _ = os.path.splitext(output_file)
            
            # Renaming the downloaded song to its proper name
            new_file = "\\".join(base.split("\\")[:-1]) + f"\\{song_name.strip('?!@#$%^&*():;')}.mp3"
            os.rename(output_file, new_file)

        # If song is not alreaded segmented
        if not (os.path.isfile(segmented_file_path)):
            self._segment_song(downloaded_file_path, song_name, genre)


        # Track Progress
        self.completed_songs += 1
        if self.completed_songs % 2 == 0:
            printProgressBar(self.completed_songs, self.total_songs, prefix = 'Progress:', suffix = 'Complete', length = 50)

                

    def download_song(self, song_list, song_url):
        """Downloads songs using song_url youtube and saves them in the songs folder and segments them and stores them in a folder named segment_<segment_duration>
        Utilized muiltithreading for faster processing

        Args:
            song_list (list(str)): directory with genre as keys and list of song names as values
            song_url (list(str)): directory with genre as keys and list of song url as values
        """
     
        # Initlialize total songs
        self.total_songs = sum([len(song_list[genre]) for genre in song_list.keys()])

        genres = list(song_list.keys())

        for genre in genres:

            # Convert genre to a list beacuse map only accepts an iterable
            genre_list = [genre] * len(song_list[genre])

            # Divide task to each thread
            with ThreadPoolExecutor(max_workers=self.n_threads) as thread:
                thread.map(self._download_individual_song, genre_list, song_list[genre], song_url[genre])



    def _segment_song(self, song_path, filename,  genre):
        """Segments song into duration of self.SEGMENT_DURATION seconds and saves them in the songs folder

        Args:
            song_path (str): path of the song
            filename (str): name of the song
            genre (str): genre of the song
        """
       

        # Set song directory as current directory to output segmented song
        os.chdir(self.segment_folder)

        # If file type not mp3, return
        if ".mp3" not in song_path:
            return
  
        # Using ffmpeg to convert mp3 into segments of 10 seconds as .mp4
        # Converting to mp3 causes Missing Headers error
        subprocess.run(['ffmpeg', '-i', song_path, '-c', 'copy' ,'-f' ,'segment', '-segment_time', str(self.SEGMENT_DURATION) ,'-reset_timestamps' ,'1', f'{genre}_%02d_{filename}.mp4', '-loglevel', 'quiet'], shell=True)
     
        # Converting all .mp4 files to .mp3
        for filename in os.listdir(self.segment_folder):

            infilename = os.path.join(self.segment_folder,filename)
            if not os.path.isfile(infilename):
                continue
            _ = os.path.splitext(filename)
            newname = infilename.replace('.mp4', '.mp3')
            _ = os.rename(infilename, newname)
        
    

