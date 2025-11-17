
import soundfile as sf
from control import Control
from audio_signal import WavSignal
from distortion import HardClipping, Softclipping, TanhClipping, AtanClipping, AlgebraicClipping
from filters import PassbandFilter, Oversampler
from graphs import Graphs
from repeated_signals import Delay
from audio_signal import PreGain, PostGain
def process_audio_chain(
        wav_path="../Rock_Guitar.wav",
        pregain_db=20,
        use_oversampling=True,
        os_factor=4,
        umbral=0.6,
        clip_mode="simetric",
        clip_offset=0.0,
        clip_variation=0.0,
        passband_on=True,
        low_freq=1000,
        high_freq=2000,
        postgain_db=7,
        save_output=True,
        output_path="processed_hard.wav"
  ):
        # read WAV file
        wav = WavSignal.archive(wav_path)
        signal = wav.data
        fs = wav.samplerate
    
        # Pre-Gain
        pregain = PreGain(pregain_db)
        signal = pregain.apply(signal)

        # Oversampling 
        if use_oversampling:
            os = Oversampler(factor=os_factor)
            signal = os.upsample(signal)

        # Clipping / Distorsión
        effects = {
            "Tanh": TanhClipping(
                offset=clip_offset,
                variation=clip_variation,
                mode=clip_mode
            ),
            "Atan": AtanClipping(
                offset=clip_offset,
                variation=clip_variation,
                mode=clip_mode
            ),
            "Algebraic": AlgebraicClipping(
                offset=clip_offset,
                variation=clip_variation,
                mode=clip_mode
            ),
            "Hard": HardClipping(umbral=umbral,
                offset=clip_offset,
                variation=clip_variation,
                mode=clip_mode
            )
    }
        select = ["Tanh", "Atan", "Algebraic", "Hard"]
        index = 3  # Choose the desired effect index here
        clip = effects[select[index]]
    
        # select clipping method
        if clip_mode == "simetric":
            signal = clip.apply_simetric(signal)
        elif clip_mode == "cutting":
            signal = clip.apply_cutting_asimetric(signal)
        elif clip_mode == "offset":
            signal = clip.apply_asimetric_displacement(signal)

        # Anti-alias + Downsample 
        if use_oversampling:
            signal = os.downsample(signal)

 
        # Band-pass filter
        if passband_on:
            bandpass = PassbandFilter(
                low_frequency=low_freq,
                high_frequency=high_freq,
                sampling_frequency=fs
            )
            signal = bandpass.apply(signal)

        #  Post-Gain
        postgain = PostGain(postgain_db)
        signal = postgain.apply(signal)

        # Guardar WAV
        if save_output:
            sf.write(output_path, signal, fs)

        return signal    
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
       

if __name__ == "__main__":
    main() 