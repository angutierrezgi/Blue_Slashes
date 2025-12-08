import numpy as np
from audio_signal import ProcessorSignal
from filters import PassbandFilter

class RepeatedSignals(ProcessorSignal):
    def __init__(self, name, seconds = 0.5, repeats = 3, dampening = 0.6):
        super().__init__(name)
        self._seconds = seconds # Seconds the effect will be repeated
        self._repeats = repeats # Amount of times the effect will take place
        self._dampening = dampening # Percent by which the signal is dampened

    def get_seconds(self):
        return self._seconds
    def set_seconds(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("The new value should be an integer or float.")
        self._seconds = value

    def get_repeats(self):
        return self._repeats
    def set_repeats(self, value):
        if not isinstance(value, int):
            raise TypeError("The new value should be an integer")
        self._repeats = value

    def get_dampening(self):
        return self._dampening
    def set_dampening(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("The new value should be an integer or float")
        self._dampening = value

    def apply(self, signal):
        raise NotImplementedError
    
class Delay(RepeatedSignals):
    def __init__(self, dampening = 0.6, seconds=0.5, repeats=3):
        super().__init__("Delay Effect", seconds, repeats, dampening)
    
    def apply(self, signal):
        # Start with the original signal as float
        output = np.copy(signal.data).astype(float)
        for i in range(1, self._repeats + 1):
            delay_samples = int(self._seconds * signal.samplerate * i)
            # Create the delayed, dampened echo
            echo = np.zeros(delay_samples + len(signal.data), dtype=float)
            echo[delay_samples:] = output[:len(signal.data)] * (self._dampening ** i)
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
    }

    def __init__(self, ambient = "room"):
        preset = self.ambient_presets.get(ambient, self.ambient_presets["room"])
        super().__init__("Reverb Effect", preset["seconds"], preset["repeats"], preset["dampening"])
        self._wet = preset["wet"] # Amount of mix between the echoes and clean signal
        self._pre_delay = preset["pre_delay"] # Pre-delay to make the sound more natural

    def get_wet(self):
        return self._wet
    def set_wet(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("The new value should be an integer or float")
        self._wet = value

    def get_pre_delay(self):
        return self._pre_delay
    def set_pre_delay(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("The new value should be an integer or float")
        self._pre_delay = value

    def apply(self, signal):
        wet_data = np.copy(signal.data).astype(float)
        dry_data = np.copy(signal.data).astype(float)
        max_len = len(signal.data)

        for i in range(1, self._repeats + 1):
            # Adding randomness to the time and samplerate of each echo
            delay_time = self._seconds * (1 + (0.2 * np.random.randn()))
            delay_samples = int((self._pre_delay + delay_time * i) * signal.samplerate)
            # Adding randomness to the dampening
            new_damp = self._dampening ** (i * (1 + (0.1 * np.random.randn())))
            echo = np.zeros(delay_samples + len(signal.data), dtype="float")
            # Adding the passband filter to, return less of the higher frequencies
            # also, we add a randomness to the amount of frequencies of each echo
            passband = PassbandFilter(100, 2800 * (1 + (0.2 * np.random.randn())), 44100, 4)
            filtered = passband.apply(signal.data) * new_damp
            echo[delay_samples: delay_samples + len(signal.data)] = filtered
            # We match both the echo's and the output data's length 
            if len(echo) > len(wet_data):
                wet_data = np.pad(wet_data, (0, len(echo) - len(wet_data)), mode="constant")
            wet_data[:len(echo)] += echo
            max_len = max(max_len, len(echo))
        # Pad dry to match output length
        if len(wet_data) > len(dry_data):
            dry_data = np.pad(dry_data, (0, len(wet_data) - len(dry_data)), mode='constant')
        # Mix dry and wet
        result = (1 - self._wet) * dry_data + self._wet * wet_data
        # Normalize the result to prevent clipping
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val
        return result