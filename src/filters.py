from scipy.signal import butter, lfilter, firwin
from audio_signal import ProcessorSignal
import numpy as np

class PassbandFilter(ProcessorSignal):

    def __init__(self, low_frequency = 400.0, high_frequency = 4000.0, sampling_frequency = 44100, order=2):
        super().__init__("band pass filter")
        # Cutoff frequencies in Hz
        self._low_frequency = low_frequency 
        self._high_frequency = high_frequency 
        # Sampling frequency (Hz)
        self._sampling_frequency = sampling_frequency 
         # order defines the slope (dB/octave) of attenuation outside the passband
        self._order = order 

    @property
    def low_frequency(self):
        return self._low_frequency
    
    @low_frequency.setter
    def low_frequency(self, value):
        # Validation: must be positive and less than high_frequency
        if value <= 0:
            raise ValueError("Low frequency must be positive")
        if value >= self._high_frequency:
            raise ValueError("Low frequency must be less than high frequency")
        self._low_frequency = float(value)
        print(f"Filter low frequency set to: {value} Hz")
    
    @property
    def high_frequency(self):
        return self._high_frequency
    
    @high_frequency.setter
    def high_frequency(self, value):
        # Validation: must be greater than low_frequency and less than Nyquist
        nyquist = self._sampling_frequency / 2
        if value <= self._low_frequency:
            raise ValueError("High frequency must be greater than low frequency")
        if value >= nyquist:
            raise ValueError(f"High frequency must be less than Nyquist ({nyquist} Hz)")
        self._high_frequency = float(value)
        print(f"Filter high frequency set to: {value} Hz")
    
    @property
    def order(self):
        return self._order
    
    @order.setter
    def order(self, value):
        # Validation: must be a positive integer
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Order must be a positive integer")
        self._order = value
        print(f"Filter order set to: {value}")
    
    def apply(self, signal):
        # Normalize cutoff frequencies by Nyquist frequency (fs/2), between 0 and 1
        signal = np.asarray(signal, dtype=float) # ensure signal is float array
        nyquist = 0.5 * self._sampling_frequency
        low = self._low_frequency / nyquist
        high = self._high_frequency / nyquist

        # looks for coefficients that define the filter response in butterworth equation
        # b and a are the numerator and denominator vectors of the filter
        b, a = butter(self._order, [low, high], btype='band')
        # applies the filter with the coefficient values ​​at the respective frequency to the signal
        # Here the frequencies outside the limit are attenuated according to the value in dB, limits in -3dB, then they fall according to the order
        signal_filtered = lfilter(b, a, signal)
        return np.asarray(signal_filtered, dtype=float)

# oversampler class that increases the sample rate of the signal by a given factor, for better non-lineal processing 
class Oversampler(ProcessorSignal):
    def __init__(self, factor=4, filter_length=101):
        super().__init__("oversampler")
        self.factor = factor
        self.filter_length = filter_length

        # Same low-pass FIR filter is used for both anti-imaging (after upsampling)
        # and anti-aliasing (before downsampling).
        self.lpf = firwin(numtaps=self.filter_length,
            cutoff=1/self.factor,     # Normalized cutoff = 1/L
            window="hamming"
        )

    def upsample(self, signal):
        # Zero-insertion upsampling by factor L
        x = np.asarray(signal, dtype=float)
        up = np.zeros(len(x) * self.factor)
        up[::self.factor] = x
        filter = lfilter(self.lpf, 1.0, up)
        # Apply low-pass filter to remove imaging components
        return np.asarray(filter, dtype=float)

    def downsample(self, signal):
        x = np.asarray(signal, dtype=float)
        # Low-pass filter to prevent aliasing before decimation
        filtered = lfilter(self.lpf, 1.0, x)
        y = filtered[::self.factor]
        # Take one sample every L samples
        return np.asarray(y, dtype=float)