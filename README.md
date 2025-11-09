# Blue_Slashes - Efectos de Pedal
Este repositorio contiene el proyecto para la materia de Programación Orientada a Objetos (POO), semestre 2025-2. En este caso se busca crear un código con base en el paradigma de la POO, para simular los efectos de una pedalera de guitarra. Algunos de los efectos buscados a trabajar son, la distorsión, el delay, el chorus, y un ecualizador (?).

## Diagrama de Clases
El siguiente diagrama, representa la estructuración del paquete de código hasta el momento:
```mermaid
classDiagram
    class WavSignal {
	    +arr data
	    +int samplerate[Hz]
	    +str route
	    +time()
	    +archive(route)
	    +normalize()
    }

    class ProcessorSignal {
	    +str name
	    +apply(WavSignal)
    }

    class PassbandFilter {
	    +float low_frequency
	    +float high_frequency
	    +float sampling_frequency
	    +int order
	    +apply(WavSignal)
    }

    class Distortion {
	    +str name
	    +str mode
	    +float gain
	    -float umbral
	    -float variation
	    -float offset
	    +apply(WavSignal)
	    +apply_simetric()
	    +apply_asimetric_cutting()
	    +apply_asimetric_displacement()
    }

    class HardClipping {
	    +str name
	    +str mode
	    +float gain
	    -float umbral
	    -float variation
	    -float offset
	    +apply_simetric()
	    +apply_asimetric_cutting()
	    +apply_asimetric_displacement()
    }

    class SoftClipping {
	    +str name
	    +str mode
	    +float gain
	    -float umbral
	    -float variation
	    -float offset
	    -limit_asimetric_cuts()
    }

    class ClippingTanh {
	    +str name
	    +str mode
	    +float gain
	    -float umbral
	    -float variation
	    -float offset
	    +apply_simetric()
	    +apply_asimetric_cutting()
	    +apply_asimetric_displacement()
    }

    class ClippingAtan {
	    +str name
	    +str mode
	    +float gain
	    -float umbral
	    -float variation
	    -float offset
	    +apply_simetric()
	    +apply_asimetric_cutting()
	    +apply_asimetric_displacement()
    }

    class ClippingAlgebraic {
	    +str name
	    +str mode
	    +float gain
	    -float umbral
	    -float variation
	    -float offset
	    +apply_simetric()
	    +apply_asimetric_cutting()
	    +apply_asimetric_displacement()
    }

    ProcessorSignal <-- WavSignal
    ProcessorSignal <|-- PassbandFilter
    ProcessorSignal <|-- Distortion
    Distortion <|-- HardClipping
    Distortion <|-- SoftClipping
    SoftClipping <|-- ClippingTanh
    SoftClipping <|-- ClippingAtan
    SoftClipping <|-- ClippingAlgebraic
```
