

class SongDownloader:
    def __init__(self):
        
        # Duration for each segmented clip
        self.SEGMENT_DURATION = 20 # Seconds

        # Get root path of the project and initialize song directory
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

    def download_song(self, song_list, song_url):
        """Downloads songs using song_url youtube and saves them in the songs folder
        Also calls _segment_song() to divide song into multiple segments of specified duration

        Args:
            song_list (list(str)): directory with genre as keys and list of song names as values
            song_url (list(str)): directory with genre as keys and list of song url as values
        """
        from pytube import YouTube
        import os

        for genre in song_list.keys():
            songs = song_list[genre]
            urls = song_url[genre]
            count = 0
            for song, url in zip(songs, urls):
                count +=1

                # If song is already downloaded
                if (os.path.isfile(self.song_dir_path + "\\" + song.strip('?!@#$%^&*():;') + ".mp3")):
                    print(f"{count}: {song} already downloaded")
                    continue


                yt = YouTube(url)
                # Get the audio stream
                audio = yt.streams.filter(only_audio=True).first()
               
                output_file = audio.download(output_path=self.song_dir_path)

               

                # Absolute path of downloaded song
                base, _ = os.path.splitext(output_file)
                
                new_file = "\\".join(base.split("\\")[:-1]) + f"\\{song.strip('?!@#$%^&*():;')}.mp3"


                try:
                    os.rename(output_file, new_file)
                    print(f"{count}: {song} downloaded")
                    self._segment_song(new_file, song, genre)
                except FileNotFoundError:
                    print(f"{count}: {song} couldn't be downloaded")
                


    def _segment_song(self, song_path, filename,  genre):
        """Segments song into duration of self.SEGMENT_DURATION seconds and saves them in the songs folder

        Args:
            song_path (str): path of the song
            filename (str): name of the song
            genre (str): genre of the song
        """
       

        import subprocess
        import os

        # Set song directory as current directory 
        os.chdir(self.song_dir_path)
        
        # If file type not mp3, return
        if ".mp3" not in song_path:
            return

        # Using ffmpeg to convert mp3 into segments of 10 seconds as .mp4
        # Converting to mp3 causes Missing Headers error
        subprocess.call(['ffmpeg', '-i', song_path, '-c', 'copy' ,'-f' ,'segment', '-segment_time', str(self.SEGMENT_DURATION) ,'-reset_timestamps' ,'1', f'{genre}_%02d_{filename}.mp4'])
        
        # Converting all .mp4 files to .mp3
        for filename in os.listdir(self.song_dir_path):

            infilename = os.path.join(self.song_dir_path,filename)
            if not os.path.isfile(infilename):
                continue
            oldbase = os.path.splitext(filename)
            newname = infilename.replace('.mp4', '.mp3')
            output = os.rename(infilename, newname)
        
    



if __name__ == "__main__":




    # from APICall import APICall
    # ac = APICall(["rock", "metal"], 50)
    # song_list = ac.get_song_list()
    # song_url = ac.get_song_url()
    # print(song_list)
    # print(song_url)

    song_list =  {'rock': ["I Ain't Worried", 'Sweater Weather', '505', 'Mr. Brightside', 'She Had Me At Heads Carolina', 'Enemy (with JID) - from the series Arcane League of Legends', 'Cigarette Daydreams', "World's Smallest Violin", 'Everybody Talks', 'Tongue Tied', 'Riptide', 'Electric Love', 'Daddy Issues', 'Softcore', 'Chicken Fried', 'House of Memories', 'Seven Nation Army', 'Counting Stars', 'Brazil', 'Shut Up and Dance', 'Fancy Like', 'Alien Blues', 'Pumped Up Kicks', 'She Likes It (feat. Jake Scott)', 'The Middle', 'Believer', "Why'd You Only Call Me When You're High?", 'Out of My League', "Drunk (And I Don't Wanna Go Home)", 'Island In The Sun', 'Kilby Girl', "Sugar, We're Goin Down", 'Separate Ways (Worlds Apart) - Bryce Miller/Alloy Tracks Remix', 'Last Night Lonely', 'Do I Wanna Know?', 'Looking Out for You', 'Stressed Out', 'You Get Me So High', 'Sex on Fire', 'Classic', 'Pompeii', 'Best Day Of My Life', 'Stick Season', 'Thunder', 'Little Dark Age', 'Can I Call You Tonight?', 'Crazy Train', 'Demons', 'Bang!', 'I Write Sins Not Tragedies'], 'metal': ['Chop Suey!', 'In the End', 'Kryptonite', 'Crazy Train', 'Paralyzer', 'Last Resort', 'Duality', 'Can You Feel My Heart', 'Numb', 'Change (In the House of Flies)', 'All Summer Long', "You're Gonna Go Far, Kid", 'Toxicity', 'Bring Me To Life', 'Animal I Have Become', 'How You Remind Me', "Can't Stop", 'Fake It', 'Hail to the King', 'Bodies', 'Down with the Sickness', 'Popular Monster', "What I've Done", 'Headstrong', 'Coming Undone', 'One Step Closer', 'Bad Company', 'Rockstar', 'Custer', 'Master of Puppets', 'Smooth Criminal', 'The Diary of Jane - Single Version', 'Lips Of An Angel', 'Sextape', 'Before I Forget', 'Addicted', 'King For A Day', 'Dani California', 'Aerials', 'The Reason', 'I Hate Everything About You', 'I Will Not Bow', 'sTraNgeRs', 'B.Y.O.B.', 'Snow (Hey Oh)', 'Monster', 'Riot', 'Voices In My Head', "It's Been Awhile", 'Bleed It Out']}
    song_url = {'rock': ['https://www.youtube.com/watch?v=42oK5vjD2UU', 'https://www.youtube.com/watch?v=lE-GhpoL3c4', 'https://www.youtube.com/watch?v=bFJvsIi05Dc', 'https://www.youtube.com/watch?v=UFKf08us2AI', 'https://www.youtube.com/watch?v=2w_Ccpwbxgc', 'https://www.youtube.com/watch?v=tOZV4tIcE7k', 'https://www.youtube.com/watch?v=jrsxWeBgadA', 'https://www.youtube.com/watch?v=bmt1LjIpoOY', 'https://www.youtube.com/watch?v=ulNS48wPZ4Q', 'https://www.youtube.com/watch?v=uGqum1FECHA', 'https://www.youtube.com/watch?v=lYoWuaw5nSk', 'https://www.youtube.com/watch?v=7JYb9RIQxx4', 'https://www.youtube.com/watch?v=v8jJD15-E6o', 'https://www.youtube.com/watch?v=MI30X9sSYlg', 'https://www.youtube.com/watch?v=Sk5TsrmgEj4', 'https://www.youtube.com/watch?v=OOtTeOkfV8A', 'https://www.youtube.com/watch?v=WM5W5y9zb1A', 'https://www.youtube.com/watch?v=Yim4--J44gk', 'https://www.youtube.com/watch?v=vWFBVWTQNyU', 'https://www.youtube.com/watch?v=4bob1KzjYQA', 'https://www.youtube.com/watch?v=KQ-XurHfOGM', 'https://www.youtube.com/watch?v=votCkjsbGnU', 'https://www.youtube.com/watch?v=_oLzX0RPquk', 'https://www.youtube.com/watch?v=ncqauLa0oDI', 'https://www.youtube.com/watch?v=xQzS3JnZQZM', 'https://www.youtube.com/watch?v=W0DM5lcj6mw', 'https://www.youtube.com/watch?v=ddwxyI3hgz8', 'https://www.youtube.com/watch?v=kM_oLaEIcEc', 'https://www.youtube.com/watch?v=RxP4ovsTLF8', 'https://www.youtube.com/watch?v=QFrD03O3u2I', 'https://www.youtube.com/watch?v=gx2wt1vnHtk', 'https://www.youtube.com/watch?v=Ufb70h78eO4', 'https://www.youtube.com/watch?v=fJmzY8CFSG0', 'https://www.youtube.com/watch?v=jvhw7fPAHtw', 'https://www.youtube.com/watch?v=fQ17tnRrA8k', 'https://www.youtube.com/watch?v=GGVSPnk7ky8', 'https://www.youtube.com/watch?v=f1tDFtMjwAE', 'https://www.youtube.com/watch?v=AxweUMdiYao', 'https://www.youtube.com/watch?v=l8brvPd8nbc', 'https://www.youtube.com/watch?v=CsIvIryJZCQ', 'https://www.youtube.com/watch?v=m326LNIRB3k', 'https://www.youtube.com/watch?v=tTsmVFbR100', 'https://www.youtube.com/watch?v=bpU-shw1t6k', 'https://www.youtube.com/watch?v=GtEvysh1654', 'https://www.youtube.com/watch?v=RHFM6njydLs', 'https://www.youtube.com/watch?v=O2qxD7ZfYrM', 'https://www.youtube.com/watch?v=ZDZtbBZuqb0', 'https://www.youtube.com/watch?v=MA0aCUxItYA', 'https://www.youtube.com/watch?v=9e2buqBpSBU', 'https://www.youtube.com/watch?v=1CBN9fKeVB4'], 'metal': ['https://www.youtube.com/watch?v=HrQsGeKN6qk', 'https://www.youtube.com/watch?v=xubrxJwLxaI', 'https://www.youtube.com/watch?v=Tpl6ncyxLGw', 'https://www.youtube.com/watch?v=ZDZtbBZuqb0', 'https://www.youtube.com/watch?v=3ejAMB3g_b8', 'https://www.youtube.com/watch?v=-hSSiMmKQh8', 'https://www.youtube.com/watch?v=HgS_kSkZC1A', 'https://www.youtube.com/watch?v=nNbZJ-IgAEg', 'https://www.youtube.com/watch?v=8P0vKLHbtMg', 'https://www.youtube.com/watch?v=A3ImpLn46MU', 'https://www.youtube.com/watch?v=5zBEdDgA_0k', 'https://www.youtube.com/watch?v=zEZRKgFIkxc', 'https://www.youtube.com/watch?v=lAg6IZc_uuU', 'https://www.youtube.com/watch?v=96MiYk9VYvc', 'https://www.youtube.com/watch?v=xXDC89tZ4IQ', 'https://www.youtube.com/watch?v=Ps-mZ5BQQDY', 'https://www.youtube.com/watch?v=a66QCJ1eRko', 'https://www.youtube.com/watch?v=eIFPuHtbHck', 'https://www.youtube.com/watch?v=Bqv3xkpb0yM', 'https://www.youtube.com/watch?v=9aJ9lONBNX4', 'https://www.youtube.com/watch?v=_wA5NmQESx8', 'https://www.youtube.com/watch?v=BmaLHGtpckg', 'https://www.youtube.com/watch?v=ldNLO7pvmgo', 'https://www.youtube.com/watch?v=PdHujs6UMYw', 'https://www.youtube.com/watch?v=nfOtrFzAyCw', 'https://www.youtube.com/watch?v=MNwZ_WHhgdw', 'https://www.youtube.com/watch?v=Ta-cQFrRdoM', 'https://www.youtube.com/watch?v=LLKbtcwS6Ys', 'https://www.youtube.com/watch?v=ypAjQYLNJZI', 'https://www.youtube.com/watch?v=xnKhsTXoKCI', 'https://www.youtube.com/watch?v=RCmuTH6T7fk', 'https://www.youtube.com/watch?v=aklqFpyd56k', 'https://www.youtube.com/watch?v=jGV75S8_cpk', 'https://www.youtube.com/watch?v=A4CTVNEhXLs', 'https://www.youtube.com/watch?v=1sKHPI7xKgo', 'https://www.youtube.com/watch?v=UGAJ3G_OnkQ', 'https://www.youtube.com/watch?v=ME6RtQgBMSI', 'https://www.youtube.com/watch?v=w4Xfg_MRH10', 'https://www.youtube.com/watch?v=N-IvW6J2e80', 'https://www.youtube.com/watch?v=-F9nCQtxkRw', 'https://www.youtube.com/watch?v=BpwCJzPlz8k', 'https://www.youtube.com/watch?v=UWr4yjxNKzA', 'https://www.youtube.com/watch?v=RV2jlbHmQ5A', 'https://www.youtube.com/watch?v=7fUtD40GqGY', 'https://www.youtube.com/watch?v=NRKFJGRKxdA', 'https://www.youtube.com/watch?v=2JwmNKeweGo', 'https://www.youtube.com/watch?v=h6Ih6e79i4Q', 'https://www.youtube.com/watch?v=T0StL53GYMU', 'https://www.youtube.com/watch?v=aoeDCe0wDyQ', 'https://www.youtube.com/watch?v=znSCwbG8_L8']}





    sd = SongDownloader()
    sd.download_song(song_list, song_url)
  

# from pydub import AudioSegment
# t1 = t1 * 1000 #Works in milliseconds
# t2 = t2 * 1000
# newAudio = AudioSegment.from_wav("oldSong.wav")
# newAudio = newAudio[t1:t2]
# newAudio.export('newSong.wav', format="wav") 

    