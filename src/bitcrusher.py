# src/bitcrusher.py
import numpy as np
from audio_signal import ProcessorSignal

class BitCrusher(ProcessorSignal):
    def __init__(self, bit_depth=4, downsample_factor=8, mix=1.0, name="BitCrusher"):
        super().__init__(name)
        self.bit_depth = bit_depth
        self.downsample_factor = downsample_factor
        self.mix = mix  # 0.0 = only the dry signal, 1.0 = just the effect

    def set_bit_depth(self, bits: int):
        bits = int(bits)
        self.bit_depth = max(1, min(16, bits))

    def set_downsample_factor(self, factor: int):
        factor = int(factor)
        self.downsample_factor = max(1, factor)

    def set_mix(self, mix: float):
        mix = float(mix)
        self.mix = max(0.0, min(1.0, mix))

    # ----- internal helpers -----
    def _reduce_samplerate(self, x: np.ndarray) -> np.ndarray:
        """Sample & hold: reduces temporal resolution"""
        if self.downsample_factor <= 1:
            return x

        x = np.asarray(x, dtype=float)

        indices = np.arange(0, len(x), self.downsample_factor)
        held = x[indices]   # values we have
        y = np.repeat(held, self.downsample_factor)

        # adjusting the length
        if len(y) > len(x):
            y = y[:len(x)]
        elif len(y) < len(x):
            y = np.pad(y, (0, len(x) - len(y)), mode="edge")

        return y

    def _reduce_bit_depth(self, x: np.ndarray) -> np.ndarray:
        """Uniform quantization to 'bit_depth' bits in range [-1, 1]"""
        x = np.asarray(x, dtype=float)
        x = np.clip(x, -1.0, 1.0)

        levels = 2 ** self.bit_depth
        max_int = levels / 2 - 1

        q = np.round(x * max_int) / max_int
        return q

    def apply(self, signal):
        """
        Recieves a np.ndarray (like the other clipping effects)
        and returns a processed np.ndarray
        """
        x = np.asarray(signal, dtype=float)

        crushed = self._reduce_samplerate(x)
        crushed = self._reduce_bit_depth(crushed)

        # Mezcla wet/dry
        return (1.0 - self.mix) * x + self.mix * crushed
