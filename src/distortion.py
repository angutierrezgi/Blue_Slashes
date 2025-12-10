import numpy as np
from audio_signal import ProcessorSignal
class Distortion(ProcessorSignal):
    def __init__(self, name, umbral = 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__(name)
        self.name = name
        self.mode = mode
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
        
    
    def get_variation(self):
        return self._variation
    
    # coherent limits for variation between -0.8 and 0.8
    def set_variation(self, value):
        self._variation = max(-0.8, min(0.8, value))

    def get_offset(self):
        return self._offset
    # coherent value of displacement for offset according to limits of the signal
    def set_offset(self, value):
        self._offset = max(-0.8, min(0.8, value))    
        
class HardClipping(Distortion):
    def __init__(self, umbral=0.7, variation=0.0, offset=0.0, mode="simetric"):
        super().__init__("Hard Clipping", umbral, variation, offset, mode)
    
    
    def get_umbral(self):
        return self._umbral
    
    # coherent value specifically for hardclipping of threshold between 0.1 and 1.0
    def set_umbral(self, value):
        self._umbral = max(0.1, min(1.0, value))
       
    def get_variation(self):
        return self._variation

    # variation setter with condition specifically coherent for hardclipping between -0.8*umbral and 0.8*umbral
    def set_variation(self, value):
        variation_limit = self._umbral * 0.8
        self._variation = max(-variation_limit, min(variation_limit, value))

    def get_offset(self):
        return self._offset

    # offset setter with condition specifically coherent for hardclipping between -0.8*umbral and 0.8*umbral
    def set_offset(self, value):
        offset_limit = self._umbral * 0.8
        self._offset = max(-offset_limit, min(offset_limit, value))
    
    # simetric hard clipping, limits between -umbral and +umbral
    def apply_simetric(self, signal):
        return np.clip(np.asarray(signal, dtype = float), -self._umbral, self._umbral)
    
    # asymetric hard clipping by cutting, limits modified by variation, regardless of the thresholds already given
    def apply_cutting_asimetric(self, signal):
        if self._variation >= 0:
            negative_limit = -self._umbral + self._variation
            positive_limit = self._umbral
        elif self._variation < 0:
            positive_limit = self._umbral + self._variation    
            negative_limit = -self._umbral
        return np.clip(np.asarray(signal, dtype=float), negative_limit, positive_limit)

    # asymetric hard clipping by displacement, limits remain the same but the signal is displaced by offset
    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return np.clip(np.asarray(signal_offset, dtype=float), -self._umbral, self._umbral)
  
# type of distortion: signal proccesed by specific functions
class Softclipping(Distortion):
    def __init__(self, nombre, umbral= 1.0, variation = 0.0, offset=0.0, mode = "simetric"):
        super().__init__(nombre, umbral, variation, offset, mode)

    def _limit_asimetrics_cuts(self):
        if self._variation >= 0:
            return -self._umbral + self._variation, self._umbral
        return -self._umbral, self._umbral + self._variation      

# type of soft clipping: signal proccesed by Tanh function 
class TanhClipping(Softclipping):
    def __init__(self, umbral= 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Soft Clipping (tanh)", umbral, variation, offset, mode)

    def apply_simetric(self, signal):
        return np.tanh(np.asarray(signal, dtype=float))

    def apply_cutting_asimetric(self, signal):
        negative_limit, positive_limit = self._limit_asimetrics_cuts()
        return  np.tanh(np.clip(np.asarray(signal, dtype=float), negative_limit, positive_limit))

    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return np.tanh(np.asarray(signal_offset, dtype=float))
    
# type of soft clipping: signal proccesed by Atan function    
class AtanClipping(Softclipping):
    def __init__(self, umbral= 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Clipping Suave (atan)", umbral, variation, offset, mode)

    def apply_simetric(self, signal):
        return (2/np.pi) * np.arctan(np.asarray(signal, dtype=float))

    def apply_cutting_asimetric(self, signal):
        negative_limit, positive_limit = self._limit_asimetrics_cuts()
        return  (2/np.pi) * np.arctan(np.clip(np.asarray(signal, dtype=float), negative_limit, positive_limit))

    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return (2/np.pi) * np.arctan(np.asarray(signal_offset, dtype=float))

# type of soft clipping: signal proccesed by algebraic function   
class AlgebraicClipping(Softclipping):
    def __init__(self, umbral= 1.0, variation = 0.0, offset = 0.0, mode = "simetric"):
        super().__init__("Clipping Suave(algebraico)", umbral, variation, offset, mode)

    def apply_simetric(self, signal):
        return np.asarray(signal, dtype=float) / (1 + np.abs(np.asarray(signal, dtype=float)))

    def apply_cutting_asimetric(self, signal):
        negative_limit, positive_limit = self._limit_asimetrics_cuts()
        clip_signal = np.clip(np.asarray(signal, dtype=float), negative_limit, positive_limit)
        return  clip_signal / (1 + np.abs(clip_signal))

    def apply_asimetric_displacement(self, signal):
        signal_offset = self._offset + signal
        return np.asarray(signal_offset, dtype=float) / (1 + np.abs(np.asarray(signal_offset, dtype=float)))
