import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import soundfile as sf
from scipy.signal import butter, lfilter
from matplotlib.widgets import Button
from grafica_prueba_wav import Graphs, Control

class SenalWav:
    def __init__(self, data, samplerate):
        self.data = data
        self.samplerate = samplerate
        
    def time(self):
        return np.arange(len(self.data)) / self.samplerate
    
    @classmethod
    def archive(cls, route):
        data, samplerate = sf.read(route)
        if data.ndim > 1:
            data = data[:, 0]
        return cls(data, samplerate)  
    
    def normalize(self):
        self.data = self.data / np.max(np.abs(self.data))  

class ProcessorSignal:
    def __init__(self, name = None):
        self.name = name
    
    def apply(self, signal):
        raise NotImplementedError("subclasses have to implement it")
        
class Overdrive(ProcessorSignal):
    def __init__(self, name, gain = 1.0, umbral = 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__(name)
        self.name = name
        self.mode = mode
        self.gain = gain
        self._umbral = umbral
        self._variation = variation
        self._offset = offset
        
    def apply(self, signal):
        if self.mode == "simetric":
            return self.apply_simetric(signal)
        elif self.mode == "asimetric_cut":
            return self.apply_cutting_asimetric(signal)
        elif self.mode == "asimetric_offset":
            return self.apply_asimetric_displacement(signal)
    
    def apply_simetric(self, signal): 
        raise NotImplementedError
    def apply_cutting_asimetric(self, signal): 
        raise NotImplementedError
    def apply_asimetric_displacement(self, signal): 
        raise NotImplementedError
        
    @property
    def variation(self):
        return self._variation

    @variation.setter
    def variation(self, value):
        self._variation = max(-0.8, min(0.8, value)) 

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = max(-0.8, min(0.8, value))    
        

class HardClipping(Overdrive):
    def __init__(self, gain = 1.0, umbral=0.7 , variation=0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Hard Clipping", gain, umbral, variation, offset, mode)
    
    @property
    def umbral(self):
        return self._umbral
    
    @umbral.setter
    def umbral(self, value):
        self._umbral = max(0.1, min(1.0, value))
       
        
        
    @property
    def variation(self):
        return self._variation

    @variation.setter
    def variation(self, value):
        variation_limit = self._umbral * 0.8
        self._variation = max(-variation_limit, min(variation_limit, value))

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        offset_limit = self._umbral * 0.8
        self._offset = max(-offset_limit, min(offset_limit, value))
    
    def apply_simetric(self, signal):
        return np.clip(signal * self.gain, -self._umbral, self._umbral)
    
    def apply_cutting_asimetric(self, signal):
        if self._variation >= 0:
            negative_limit = -self._umbral + self._variation
            positive_limit = self._umbral
        elif self._variation < 0:
            positive_limit = self._umbral + self._variation    
            negative_limit = -self._umbral
        return np.clip(signal * self.gain, negative_limit, positive_limit)
    
    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal 
        return np.clip(signal_offset * self.gain, -self._umbral, self._umbral)
            
        
        

class ClippingSuave(Overdrive):
    def __init__(self, nombre, gain=1.0, umbral= 1.0, variation = 0.0, offset=0.0, mode = "simetric"):
        super().__init__(nombre, gain, umbral, variation, offset, mode)
     
    def _limit_asimetrics_cuts(self):
        if self.variation >= 0:
            return -self._umbral + self._variation, self._umbral
        return -self._umbral, self._umbral + self._variation      
    
class ClippingTanh(ClippingSuave):
    def __init__(self, gain=1.0, umbral= 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Soft Clipping (tanh)", gain, umbral, variation, offset, mode)
        
    def apply_simetric(self, signal):
        return np.tanh(signal * self.gain)
    
    def apply_cutting_asimetric(self, signal):
        negative_limit, positive_limit = self._limit_asimetrics_cuts()
        return  np.tanh(np.clip(signal * self.gain, negative_limit, positive_limit))
    
    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return np.tanh(signal_offset * self.gain)
        
        
    
class ClippingAtan(ClippingSuave):
    def __init__(self, gain=3.0, umbral= 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Clipping Suave (atan)", gain, umbral, variation, offset, mode)
        
    def apply_simetric(self, signal):
        return (2/np.pi) * np.arctan(signal * self.gain)
    
    
    def apply_cutting_asimetric(self, signal):
        negative_limit, positive_limit = self._limit_asimetrics_cuts()
        return  (2/np.pi) * np.arctan(np.clip(signal * self.gain, negative_limit, positive_limit))
    
    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return (2/np.pi) * np.arctan(signal_offset * self.gain)
    
class ClippingAlgebraico(ClippingSuave):
    def __init__(self, gain=3.0, umbral= 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Clipping Suave(algebraico)", gain, umbral, variation, offset, mode)
        
    def apply_simetric(self, signal):
        return signal / (1 + np.abs(signal * self.gain))
    
    def apply_cutting_asimetric(self, signal):
        negative_limit, positive_limit = self._limit_asimetrics_cuts()
        clip_signal = np.clip(signal * self.gain, negative_limit, positive_limit)
        return  clip_signal / (1 + np.abs(clip_signal * self.gain))
    
    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return signal_offset / (1 + np.abs(signal_offset * self.gain))
     
            
class FiltroPasabanda(ProcessorSignal):
    
    def __init__(self, low_frequency = 400.0, high_frequency = 4000.0, sampling_frequency = 44100, order=2):
        super().__init__("band pass filtre")
        self.low_frequency = low_frequency
        self.high_frequency = high_frequency
        self.sampling_frequency = sampling_frequency
        self.order = order

    def apply(self, signal):
        nyquist = 0.5 * self.sampling_frequency
        low = self.low_frequency / nyquist
        high = self.high_frequency / nyquist
        b, a = butter(self.order, [low, high], btype='band')
        signal_filtered = lfilter(b, a, signal)
        return signal_filtered

        
if __name__ == "__main__":
    guitar = SenalWav.archive(r"Blue_Slashes\Blue_Slashes\Guitar 5 LEAD 170bpm G Minor DRY.wav")
    guitar.normalize()
    
    
    hard_clipped = HardClipping(0.7)
    
    tanh_clipped = ClippingTanh(3.0)
    
    atan_clipped = ClippingAtan(5.0)
    
    algebraic_clipped = ClippingAlgebraico(7.0)
    
    filtered = FiltroPasabanda(400.0, 1000.0, guitar.samplerate, order=2)
    
    effects = {'Hard': hard_clipped , 'Tanh': tanh_clipped , 'Atan': atan_clipped, 'Algebraic': algebraic_clipped, 'Filter':
        filtered}
    
    control = Control(guitar, effects) 
    
    control.original_signal_graph(guitar.time(), guitar.data)
    control.show_control_window()
    
sf.write('guitarra_atanclipped.wav', atan_clipped.apply(guitar.data), guitar.samplerate)
sf.write('guitarra_filtered.wav', filtered.apply(atan_clipped.apply(guitar.data)), guitar.samplerate)  
"""         
sf.write('guitarra_hardclipped.wav', hard_clipped.aplicar(guitarra.data), guitarra.samplerate)
sf.write('guitarra_tanhclipped.wav', tanh_clipped.aplicar(guitarra.data), guitarra.samplerate)
sf.write('guitarra_algebraicclipped.wav', algebraic_clipped.aplicar(guitarra.data), guitarra.samplerate)"""
"""sf.write('guitarra_atanclipped.wav', atan_clipped.aplicar(guitarra.data), guitarra.samplerate)
sf.write('guitarra_filtered.wav', filtre.aplicar(atan_clipped.aplicar(guitarra.data)), guitarra.samplerate)
"""


        