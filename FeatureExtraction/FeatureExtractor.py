import os
import warnings
from concurrent.futures import ThreadPoolExecutor

import librosa
import numpy as np
import pandas as pd

from progressBar import printProgressBar

warnings.filterwarnings('ignore')
class FeatureExtractor():

    def __init__(self, segment_duration=30, n_threads=10, frame_size = 1024, hop_length = 512, split_frequency = 2000):
        """

        Args:
            segment_duration (int, optional): Dataset to be used. Uses segmented into `segment_duration` seconds. Defaults to 30.
            n_threads (int, optional): number of threads to use. Defaults to 10.
            frame_size (int, optional): .Defaults to 1024.
            hop_length (int, optional): Defaults to 512.
            split_frequency (int, optional): Split frequency for Band Energy Ratio. Defaults to 2000.
        """
        
        self.root_dir, self.song_dir = self._get_song_dir(segment_duration)
        self.features = self._create_feature_list()
        self.n_threads = n_threads
        self.frame_size = frame_size
        self.hop_length = hop_length
        self.split_frequency = split_frequency
        self.data = self._create_dataframe()

        # To keep track of progress
        self.extracted_data = 0
        self.total_data = 0
 

    def _get_song_dir(self, segment_duration):
        """Generated path of Song Directory

        Args:
            segment_duration (int): Duration of segmented song. Dataset of this duration of segmented song will be used

        Returns:
            (str, str): root directory path and song directory path
        """
        relative_song_Dir = f"SongCollection\\songs\\segment_{segment_duration}"
        root_dir = os.path.dirname(os.path.realpath(__file__)).replace("\\FeatureExtraction", "")
        song_dir = os.path.join(root_dir, relative_song_Dir)

        return root_dir, song_dir

    def _create_feature_list(self):
        """Create a list of features to be used in training

        Returns:
            List(str): Name of each feature
        """

        song_info = ["Name", "Genre"]

        # Using 13 MFCC Coefficients as it is a convention
        mfccs_features = [f"MFCC{n}" for n in range(13)]

        # Amplitude Envelope, Root Means Square, Zero Crossing Rate
        time_domain_features=  ["AE", "RMS", "ZCR"]

        # Band Energy Ratio, Spectral Centroid, Bandwidth
        frequency_domain_features = ["BER", "SC", "BW", *mfccs_features]

        # Using Mean and Standard Deviation of all individual features and modelling features
        all_features = np.array([[f"{name}_Mean", f"{name}_Std"] for name in [*time_domain_features, *frequency_domain_features]]).flatten()

        all_features = [*song_info, *all_features]
        return all_features

    def _create_dataframe(self):
        """Creates empty DataFrame

        Returns:
            DataFrame: Empty DataFrame
        """
        return pd.DataFrame(columns=self.features)
        
    def _amplitude_envelope(self, signal):
        """Calculates amplitude evnelope of a signal

        Args:
            signal (numpy array): audio signal

        Returns:
            numpy array: amplitude envelope
        """
        return np.array([max(signal[i:i+self.frame_size]) for i in range(0, len(signal), self.hop_length)])


    def _calculate_split_frequency_bins(self, spectrogram, sr):
        """Calculated split frequency bins for Band Energy Ratio

        Args:
            spectrogram (Numpy array of complex numbers): Spectrogram of the signal
            sr (int): Sampling Rate

        Returns:
            int: Split Frequency Bin
        """
        frequency_range = sr / 2
        frequency_delta_per_bin = frequency_range / spectrogram.shape[0]
        split_frequency_bin = np.floor(self.split_frequency / frequency_delta_per_bin)

        return int(split_frequency_bin)


    def _calculate_band_enery_ratio(self, spectrogram, sr):
        """Calculates Band Energy Ratio

        Args:
            spectrogram (Numpy array of complex numbers): Spectrogram
            sr (int): Sampling Rate

        Returns:
            Numpy array: Band Energy Ratio
        """
        split_frequency_bin = self._calculate_split_frequency_bins(spectrogram,  sr)

        # Move to the power spectrogram

        spec_2 = np.square(np.abs(spectrogram))
        spec_2 = spec_2.T

        # Time, Freq
        upper = [np.sum(mag[:split_frequency_bin]) for mag in spec_2]
        lower = [np.sum(mag[split_frequency_bin:]) for mag in spec_2]

        BER = np.divide(upper, lower)

        # Some values turn into NaN when divided by 0
        BER_no_nan = BER[~np.isnan(BER)]

        return BER_no_nan

    def _get_song_list(self):
        """Returns list of songs in the song directory

        Returns:
            Numpy Array: list of songs
        """
        song_list = np.array(os.listdir(self.song_dir))
        self.total_data = len(song_list)
        return song_list
    
    def _dump_data(self):
        """Dumps data into a csv file
        """
        self.data.to_csv(os.path.join(self.root_dir, 'data.csv'))

    def extract_features(self):
        """Extract features and stores it into a DataFrame and dumps it into a csv file. Used multithreading to speed up the process
        """
        song_list = self._get_song_list()
        printProgressBar(self.extracted_data, self.total_data, prefix = f'{self.extracted_data:6.0f}{self.total_data:6.0f} Progress:', suffix = 'Complete', length = 50)


        with ThreadPoolExecutor(max_workers=self.n_threads) as thread:
            thread.map(self._extract_features_per_sample, song_list)

        self._dump_data()

    def _extract_features_per_sample(self, song_name):
        """Extracts features for a single song and appends it to the DataFrame

        Args:
            song_name (str): Song Name
        """
    
        splitted_name = song_name.split("_")
        genre = splitted_name[0]
        name = " ".join(splitted_name[1:])
        song_path = os.path.join(self.song_dir, song_name)

        signal , sr = librosa.load(song_path)
        
        spectrogram = librosa.stft(signal, n_fft=self.frame_size, hop_length=self.hop_length)

        AE = self._amplitude_envelope(signal)
        RMS = librosa.feature.rms(signal, self.frame_size, self.hop_length)[0]
        ZCR = librosa.feature.zero_crossing_rate(signal, self.frame_size, self.hop_length)[0]   

        BER = self._calculate_band_enery_ratio(spectrogram, sr)
        SC = librosa.feature.spectral_centroid(y=signal, sr=sr, n_fft=self.frame_size, hop_length=self.hop_length)[0]
        BW = librosa.feature.spectral_bandwidth(y=signal, sr=sr, n_fft=self.frame_size, hop_length=self.hop_length)[0]

        MFCCs = librosa.feature.mfcc(signal, n_mfcc=13, sr=sr) # -> (13, bins)

        row_data = pd.Series([name, genre, AE.mean(), AE.std(), RMS.mean(), RMS.std(), ZCR.mean(), ZCR.std(), BER.mean(), BER.std(), SC.mean(), SC.std(), BW.mean(), BW.std(), MFCCs[0].mean(), MFCCs[0].std(), MFCCs[1].mean(), MFCCs[1].std(), MFCCs[2].mean(), MFCCs[2].std(), MFCCs[3].mean(), MFCCs[3].std(), MFCCs[4].mean(), MFCCs[4].std(), MFCCs[5].mean(), MFCCs[5].std(), MFCCs[6].mean(), MFCCs[6].std(), MFCCs[7].mean(), MFCCs[7].std(), MFCCs[8].mean(), MFCCs[8].std(), MFCCs[9].mean(), MFCCs[9].std(), MFCCs[10].mean(), MFCCs[10].std(), MFCCs[11].mean(), MFCCs[11].std(), MFCCs[12].mean(), MFCCs[12].std()], index=self.features)
        self.data = pd.concat([self.data, row_data.to_frame().T], ignore_index=True)

        self.extracted_data += 1
        if self.extracted_data % 100 == 0:
            self._dump_data()
            printProgressBar(self.extracted_data, self.total_data, prefix = f'{self.extracted_data:6.0f}{self.total_data:6.0f} Progress:', suffix = 'Complete', length = 50)
        
