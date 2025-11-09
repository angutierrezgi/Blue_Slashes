import numpy as np
from audio_signal import ProcessorSignal
class Distortion(ProcessorSignal):
    def __init__(self, name, gain = 1.0, umbral = 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__(name)
        self.name = name
        self.mode = mode
        self.gain = gain # multiply input signal by gain factor
        self._umbral = umbral # treshold value of the signal for clipping
        self._variation = variation # variation for asymetric clipping, reduces one of the limits
        self._offset = offset # offset for asymetric clipping, displaces the signal up or down
        
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
    
    # coherent limits for variation between -0.8 and 0.8
    @variation.setter
    def variation(self, value):
        self._variation = max(-0.8, min(0.8, value)) 

    @property
    def offset(self):
        return self._offset
    # coherent value of displacement for offset according to limits of the signal
    @offset.setter
    def offset(self, value):
        self._offset = max(-0.8, min(0.8, value))    
        

class HardClipping(Distortion):
    def __init__(self, gain = 1.0, umbral=0.7 , variation=0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Hard Clipping", gain, umbral, variation, offset, mode)
    
    @property
    def umbral(self):
        return self._umbral
    
    # coherent value specifically for hardclipping of threshold between 0.1 and 1.0
    @umbral.setter
    def umbral(self, value):
        self._umbral = max(0.1, min(1.0, value))
       
        
        
    @property
    def variation(self):
        return self._variation

    # variation setter with condition specifically coherent for hardclipping between -0.8*umbral and 0.8*umbral
    @variation.setter
    def variation(self, value):
        variation_limit = self._umbral * 0.8
        self._variation = max(-variation_limit, min(variation_limit, value))

    @property
    def offset(self):
        return self._offset

    # offset setter with condition specifically coherent for hardclipping between -0.8*umbral and 0.8*umbral    
    @offset.setter
    def offset(self, value):
        offset_limit = self._umbral * 0.8
        self._offset = max(-offset_limit, min(offset_limit, value))
    
    # simetric hard clipping, limits between -umbral and +umbral
    def apply_simetric(self, signal):
        return np.clip(signal * self.gain, -self._umbral, self._umbral)
    
    # asymetric hard clipping by cutting, limits modified by variation, regardless of the thresholds already given
    def apply_cutting_asimetric(self, signal):
        if self._variation >= 0:
            negative_limit = -self._umbral + self._variation
            positive_limit = self._umbral
        elif self._variation < 0:
            positive_limit = self._umbral + self._variation    
            negative_limit = -self._umbral
        return np.clip(signal * self.gain, negative_limit, positive_limit)
    
    # asymetric hard clipping by displacement, limits remain the same but the signal is displaced by offset
    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal 
        return np.clip(signal_offset * self.gain, -self._umbral, self._umbral)
            
        
        
# type of distortion: signal proccesed by specific functions
class Softclipping(Distortion):
    def __init__(self, nombre, gain=1.0, umbral= 1.0, variation = 0.0, offset=0.0, mode = "simetric"):
        super().__init__(nombre, gain, umbral, variation, offset, mode)
     
    def _limit_asimetrics_cuts(self):
        if self.variation >= 0:
            return -self._umbral + self._variation, self._umbral
        return -self._umbral, self._umbral + self._variation      

# type of soft clipping: signal proccesed by Tanh function 
class TanhClipping(Softclipping):
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
        
        
# type of soft clipping: signal proccesed by Atan function    
class AtanClipping(Softclipping):
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

# type of soft clipping: signal proccesed by algebraic function   
class AlgebraicClipping(Softclipping):
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
     
