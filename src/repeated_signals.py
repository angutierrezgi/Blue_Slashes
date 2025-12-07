import numpy as np
from audio_signal import ProcessorSignal
from filters import PassbandFilter

class RepeatedSignals(ProcessorSignal):
    def __init__(self, name, seconds = 0.5, repeats = 3):
        super().__init__(name)
        self.seconds = seconds # Seconds the effect will be repeated
        self.repeats = repeats # Amount of times the effect will take place

    def apply(self, signal):
        raise NotImplementedError
    
class Delay(RepeatedSignals):
    def __init__(self, dampening = 0.6, seconds=0.5, repeats=3):
        super().__init__("Delay Effect", seconds, repeats)
        self.dampening = dampening # Percentage in which the effect is dampened by
    
    def apply(self, signal):
        # Start with the original signal as float
        output = np.copy(signal.data).astype(float)
        for i in range(1, self.repeats + 1):
            delay_samples = int(self.seconds * signal.samplerate * i)
            # Create the delayed, dampened echo
            echo = np.zeros(delay_samples + len(signal.data), dtype=float)
            echo[delay_samples:] = output[:len(signal.data)] * (self.dampening ** i)
            # Pad output if needed
            if len(echo) > len(output):
                output = np.pad(output, (0, len(echo) - len(output)), mode='constant')
            # Add echo to output
            output[:len(echo)] += echo
        # Normalize to prevent clipping
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val
        return output
    
class Reverb(RepeatedSignals):
    ambient_presets = {
        "room":      {"dampening": 0.5, "seconds": 0.01, "repeats": 8,  "wet": 0.4, "pre_delay": 0.02},
        "hall":      {"dampening": 0.6, "seconds": 0.04, "repeats": 12, "wet": 0.5, "pre_delay": 0.055},
        "cathedral": {"dampening": 0.7, "seconds": 0.05, "repeats": 20, "wet": 0.6, "pre_delay": 0.1},
        "canyon":    {"dampening": 0.8, "seconds": 0.09,  "repeats": 25, "wet": 0.7, "pre_delay": 0.15},
        # Add more as needed
    }

    def __init__(self, ambient="room", pre_delay = 0.02):
        preset = self.ambient_presets.get(ambient, self.ambient_presets["room"])
        super().__init__("Reverb Effect", preset["seconds"], preset["repeats"])
        self.dampening = preset["dampening"]
        self.wet = preset["wet"]
        self.pre_delay = preset["pre_delay"]

    def apply(self, signal):
        # delay = Delay(self.dampening, self.seconds, self.impact)
        # passband = PassbandFilter(100, 9000, 44100, 4)
        # signal_delay = delay.apply(signal)
        # signal_applied = passband.apply(signal_delay)
        # # Pad dry signal to match wet length
        # dry = signal.data.astype(float)
        # if len(signal_applied) > len(dry):
        #     dry = np.pad(dry, (0, len(signal_applied) - len(dry)), mode='constant')
        # output = (1 - self.wet) * dry + self.wet * signal_applied
        # return output
        wet_data = np.copy(signal.data).astype(float)
        dry_data = np.copy(signal.data).astype(float)
        max_len = len(signal.data)

        for i in range(1, self.repeats + 1):
            # adding randomness to the time and samplerate of each echo
            delay_time = self.seconds * (1 + (0.2 * np.random.randn()))
            delay_samples = int((self.pre_delay + delay_time * i) * signal.samplerate)
            # adding randomness to the dampening
            new_damp = self.dampening ** (i * (1 + (0.1 * np.random.randn())))
            echo = np.zeros(delay_samples + len(signal.data), dtype="float")
            # adding the passband filter to, return less of the higher frequencies
            # also, we add a randomness to the amount of frequencies of each echo
            passband = PassbandFilter(100, 2800 * (1 + (0.2 * np.random.randn())), 44100, 4)
            filtered = passband.apply(signal.data) * new_damp
            echo[delay_samples: delay_samples + len(signal.data)] = filtered
            # We match both the echo's and the output data's length 
            if len(echo) > len(wet_data):
                wet_data = np.pad(wet_data, (0, len(echo) - len(wet_data)), mode="constant")
            wet_data[:len(echo)] += echo
            max_len = max(max_len, len(echo))
        # pad dry to match output length
        if len(wet_data) > len(dry_data):
            dry_data = np.pad(dry_data, (0, len(wet_data) - len(dry_data)), mode='constant')
        # Mix dry and wet
        result = (1 - self.wet) * dry_data + self.wet * wet_data
        # Normalize
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val
        return result