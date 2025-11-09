from scipy.signal import butter, lfilter
from signal import ProcessorSignal

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