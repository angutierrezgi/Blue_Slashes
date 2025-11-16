import soundfile as sf
from control import Control
from audio_signal import WavSignal
from distortion import HardClipping, Softclipping, TanhClipping, AtanClipping, AlgebraicClipping
from filters import PassbandFilter
from graphs import Graphs
from repeated_signals import Delay

def main():
    guitar = WavSignal.archive('../Guitar G minor 170bpm.wav')
    guitar.normalize()
    
    hard_clipped = HardClipping(15.0)

    tanh_clipped = TanhClipping(7.0)


    atan_clipped = AtanClipping(gain=3.0, mode="asimetric_cut")
    atan_clipped_cut = AtanClipping(3.0)        
    atan_clipped_cut.set_variation(5.0)
    atan_clipped_cut.set_offset(0.0)
  


    algebraic_clipped = AlgebraicClipping(7.0)

    delay_effect = Delay(0.73, 0.176, 4)

    filtered = PassbandFilter(200.0, 1500.0, guitar.samplerate, order=4)
    
    effects = {'Hard': hard_clipped ,
               'Tanh': tanh_clipped ,
               'Atan': atan_clipped,
               'Algebraic': algebraic_clipped,
               'Filter': filtered}

    
    control = Control(guitar, effects) 
    
    
    control.show_control_window()
    sf.write('guitarra_original_filtered.wav', filtered.apply(guitar.data), guitar.samplerate)
    sf.write('guitarra_attanclipped_cut_filtered.wav', filtered.apply(atan_clipped_cut.apply(guitar.data)), guitar.samplerate)
    sf.write('guitarra_atanclipped.wav', atan_clipped.apply(guitar.data), guitar.samplerate)
    sf.write('guitarra_atanclipped_cut.wav', atan_clipped_cut.apply(guitar.data), guitar.samplerate)
    sf.write('guitarra_filtered.wav', filtered.apply(atan_clipped.apply(guitar.data)), guitar.samplerate)
    sf.write('guitarra_delay.wav',delay_effect.apply(guitar), guitar.samplerate)
    sf.write('guitarra_hardclipped.wav', hard_clipped.apply(guitar.data), guitar.samplerate)
    sf.write('guitarra_hardclipped_filtered.wav', filtered.apply(hard_clipped.apply(guitar.data)), guitar.samplerate)  
    
if __name__ == "__main__":
    main()