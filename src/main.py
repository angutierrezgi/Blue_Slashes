
import soundfile as sf
from control import Control
from audio_signal import WavSignal
from distortion import HardClipping, Softclipping, TanhClipping, AtanClipping, AlgebraicClipping
from filters import PassbandFilter, Oversampler
from graphs import Graphs
from repeated_signals import Delay, Reverb, Reverb
from audio_signal import PreGain, PostGain  
from bitcrusher import BitCrusher  # <-- NUEVO
   
def main():

    pregain = PreGain()
    oversampler = Oversampler()
    hard_clipped = HardClipping()
    tanh_clipped = TanhClipping()
    atan_clipped = AtanClipping()
    algebraic_clipped = AlgebraicClipping()
    delay_effect = Delay(0.24, 0.705, 4)
    passband = PassbandFilter(500, 2000, 44100, order=4)
    postgain = PostGain()
    bitcrusher = BitCrusher(bit_depth=4, downsample_factor=8, mix=1.0)
    reverb = Reverb("canyon")
    effects = {'Hard': hard_clipped ,
               'Tanh': tanh_clipped ,
               'Atan': atan_clipped,
               'Algebraic': algebraic_clipped,
               'Filter': passband,
               'Delay': delay_effect,
               'Oversampler': oversampler,
               'PreGain': pregain,
               'PostGain': postgain,
               'BitCrusher': bitcrusher, 
               'Reverb': reverb
               }

    control = Control(effects) 
    control.show_control_window()
       

if __name__ == "__main__":
    main()