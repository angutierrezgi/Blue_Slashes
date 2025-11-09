import soundfile as sf
from control import Control
from audio_signal import WavSignal
from distortion import HardClipping, Softclipping, TanhClipping, AtanClipping, AlgebraicClipping
from filters import PassbandFilter
from graphs import Graphs
from repeated_signals import Delay

def main():
    guitar = WavSignal.archive('Guitar G minor 170bpm.wav')
    guitar.normalize()
    
    hard_clipped = HardClipping(3.0)

    tanh_clipped = TanhClipping(7.0)

    atan_clipped = AtanClipping(5.0)

    algebraic_clipped = AlgebraicClipping(7.0)

    delay_effect = Delay(0.73, 0.176, 4)

    filtered = PassbandFilter(1000.0, 2000.0, guitar.samplerate, order=2)
    
    effects = {'Hard': hard_clipped ,
               'Tanh': tanh_clipped ,
               'Atan': atan_clipped,
               'Algebraic': algebraic_clipped,
               'Filter': filtered}

    
    control = Control(guitar, effects) 
    
    
    control.show_control_window()
    sf.write('guitarra_atanclipped.wav', atan_clipped.apply(guitar.data), guitar.samplerate)
    sf.write('guitarra_filtered.wav', filtered.apply(atan_clipped.apply(guitar.data)), guitar.samplerate)
    sf.write('guitarra_delay.wav',delay_effect.apply(guitar), guitar.samplerate)
       
    
if __name__ == "__main__":
    main()