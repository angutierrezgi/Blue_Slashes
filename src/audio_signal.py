import numpy as np
import soundfile as sf
from scipy.signal import spectrogram as spectrogrameam

# class that represents a .wav signal
class WavSignal:
    def __init__(self, data, samplerate):
        self.data = data
        self.samplerate = samplerate
        
    # It creates the class with the path of the .wav file directly and generates the 
    # data and sample rate, and if the signal vector is stereo, it converts it to mono.
    @classmethod
    def archive(cls, route):   
        data, samplerate = sf.read(route)
        if data.ndim > 1:
            data = data[:, 0]
        return cls(data, samplerate)  
        
    # normalize the signal by multiplying the vector by the multiplicative inverse 
    # of the maximum value of the vector itself
    # to the range [-1, 1]
    def normalize(self):
        self.data = self.data / np.max(np.abs(self.data))  
     
        
# class reserved for classes that process the signal in some way to inherit it
class ProcessorSignal:
    def __init__(self, name = None):
        self.name = name
    
    def apply(self, signal):
        raise NotImplementedError("subclasses have to implement it")

class PreGain(ProcessorSignal):

    def __init__(self, gain_db=1):
        super().__init__("pre-gain")
        self._gain_db = gain_db
        
    def set_gain(self, gain_db):
        if gain_db > 40:
            self._gain_db = 40
        elif gain_db < 1:
            self._gain_db = 1
        else:
            self._gain_db = gain_db

    def apply(self, signal):
        gain = 10 ** (self._gain_db / 20)
        return np.asarray(signal * gain, dtype=float)

class PostGain(ProcessorSignal):

    def __init__(self, gain_db= 1):
        super().__init__("post-gain")
        self._post_gain_db = gain_db

    def set_gain(self, gain_db):
        if gain_db > 20:
            self._post_gain_db = 20
        elif gain_db < -20:
            self._post_gain_db = -20
        else:
            self._post_gain_db = gain_db

    def apply(self, signal):
        gain = 10 ** (self._post_gain_db / 20)
        return np.asarray(signal, dtype = float) * gain
    

# methods for graphing signals
# method to generate time axis based on samplerate and data length
def time_x(data, samplerate):
    data = np.asarray(data)
    return np.arange(len(data)) / samplerate

# fft method that returns frequencies and magnitude
def fft(data, samplerate, freq_min=0, freq_max=4000):
    n = len(data) # number of samples
    d = 1 / samplerate # sample spacing
    fft_values = np.fft.rfft(data) # compute the FFT for real input
    frequencies = np.fft.rfftfreq(n, d=d) # corresponding frequencies
    magnitude = np.abs(fft_values) / n * 2 # normalize the magnitude between 0 and 1
    limits_graphing = (frequencies >= freq_min) & (frequencies <= freq_max)
    return frequencies[limits_graphing], magnitude[limits_graphing]
    
    # spectrogram method that returns frequency, time and spectrum in dB
def spectrogram(data, samplerate):
    f, t, spectrum = spectrogrameam(data, samplerate) # computes the spectrogram
    spectrum = 20 * np.log10(spectrum + 1e-12) # formula to convert to decibels (dB)
    return f, t, spectrum