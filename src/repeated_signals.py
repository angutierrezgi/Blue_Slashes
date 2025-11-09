import numpy as np
from audio_signal import ProcessorSignal

class RepeatedSignals(ProcessorSignal):
    def __init__(self, name, seconds = 0.5, impact = 3):
        super().__init__(name)
        self.seconds = seconds # Seconds the effect will be repeated
        self.impact = impact # Amount of times the effect will take place

    def apply(self, signal):
        raise NotImplementedError
    
class Delay(RepeatedSignals):
    def __init__(self, dampening = 0.6, seconds=0.5, impact=3):
        super().__init__("Delay Effect", seconds, impact)
        self.dampening = dampening # Percentage in which the effect is dampened by
    
    def apply(self, signal):
        # We copy the original data as an array of floats
        output = np.copy(signal.data).astype(float)

        for i in range(1, self.impact +1):
            # Convert the seconds to samplerate (Hz)
            delay_samples = int(self.seconds * signal.samplerate * i)

            # Creates an array of zeros (seconds of silence) according to the delay provided
            # and unites it with the dampened signal
            silent_padding = np.zeros(delay_samples, dtype=signal.data.dtype)
            delayed_data = np.concatenate((silent_padding, signal.data * (self.dampening ** i)))

            # Makes both audio signals have the same length, by adding to the original
            # or cutting from this one as well
            if len(delayed_data) >= len(signal.data):
                output = np.concatenate((signal.data, np.zeros(len(delayed_data) - len(signal.data), dtype=signal.data.dtype)))
            else:
                output = signal.data[:len(delayed_data)]

            # Adds the delayed audio signal to the expected output, so that it has the effect
            # applied 'impact' amount of times
            output[:len(delayed_data)] += delayed_data
            
        return output