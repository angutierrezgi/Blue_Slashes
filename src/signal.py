import numpy as np
import soundfile as sf
from scipy.signal import spectrogram
# class that represents a .wav signal
class WavSignal:
    def __init__(self, data, samplerate):
        self.data = data
        self.samplerate = samplerate
        
    
    
    # method to generate time axis based on samplerate and data length
    def time(self):
        return np.arange(len(self.data)) / self.samplerate
    
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
     
    def fft(self, data, samplerate):
        n = len(data)
        d = 1 / samplerate
        fft_values = np.fft.rfft(data)
        frequencies = np.fft.rfftfreq(n, d=d)
        magnitude = np.abs(fft_values) / n * 2
        
   
        return frequencies, magnitude

    def spectrogram(self, data, samplerate):
        f, t, spectrum = spectrogram(data, samplerate)
        spectrum = 10 * np.log10(spectrum + 1e-12)
        return f, t, spectrum
        
# class reserved for classes that process the signal in some way to inherit it
class ProcessorSignal:
    def __init__(self, name = None):
        self.name = name
    
    def apply(self, signal):
        raise NotImplementedError("subclasses have to implement it")
    

    