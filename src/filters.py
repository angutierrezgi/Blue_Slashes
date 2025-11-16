from scipy.signal import butter, lfilter, firwin
from audio_signal import ProcessorSignal
import numpy as np

class PassbandFilter(ProcessorSignal):
    
    def __init__(self, low_frequency = 400.0, high_frequency = 4000.0, sampling_frequency = 44100, order=2):
        super().__init__("band pass filter")
        # Cutoff frequencies in Hz
        self.low_frequency = low_frequency 
        self.high_frequency = high_frequency 
        # Sampling frequency (Hz)
        self.sampling_frequency = sampling_frequency 
         # order defines the slope (dB/octave) of attenuation outside the passband
        self.order = order 

    def apply(self, signal):
        # Normalize cutoff frequencies by Nyquist frequency (fs/2), between 0 and 1
        nyquist = 0.5 * self.sampling_frequency
        low = self.low_frequency / nyquist 
        high = self.high_frequency / nyquist 
        
        # looks for coefficients that define the filter response in butterworth equation
        # b and a are the numerator and denominator vectors of the filter 
        b, a = butter(self.order, [low, high], btype='band')
        # applies the filter with the coefficient values ​​at the respective frequency to the signal
        # Here the frequencies outside the limit are attenuated according to the value in dB, limits in -3dB, then they fall according to the order
        signal_filtered = lfilter(b, a, signal)
        return signal_filtered

# oversampler class that increases the sample rate of the signal by a given factor, for better non-lineal processing 
class Oversampler(ProcessorSignal):
    def __init__(self, factor=4, filter_length=101):
        super().__init__("oversampler")
        self.factor = factor
        self.filter_length = filter_length
        # Design low-pass FIR filter for interpolation/decimation
        self.lpf = firwin(numtaps=self.filter_length, cutoff=1/self.factor, window="hamming")

    def apply(self, signal):
        """Upsample the input signal by self.factor, apply low-pass filter to remove images."""
        # Insert zeros to increase sample rate
        upsampled = np.zeros(len(signal) * self.factor)
        upsampled[::self.factor] = signal
        # Apply low-pass filter to remove imaging
        filtered = lfilter(self.lpf, 1.0, upsampled)
        return filtered

    def downsample(self, signal):
        """Low-pass filter and reduce sample rate by self.factor."""
        filtered = lfilter(self.lpf, 1.0, signal)
        downsampled = filtered[::self.factor]
        return downsampled