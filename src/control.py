import numpy as np
from matplotlib.widgets import Button
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from graphs import Graphs
from audio_signal import WavSignal

class Control:
    def __init__(self, guitar, effects, style='dark_background'):
        plt.style.use(style) # assigns a style to the plots
        self.guitar = guitar
        self.effects = effects
       
        # creates principal window "Control" and assings to it rows and columns
        self.control = plt.figure(figsize=(12,4), edgecolor='black') 
        self.gs = GridSpec(2, 1, figure=self.control)
        
        # assings positions to buttoms for add to the control window 
        ax_original = self.control.add_axes([0.4, 0.80, 0.2, 0.1])
        ax_hard = self.control.add_axes([0.1, 0.05, 0.35, 0.1])
        ax_tanh = self.control.add_axes([0.6, 0.20, 0.35, 0.1])
        ax_atan = self.control.add_axes([0.6, 0.05, 0.35, 0.1])
        ax_alg  = self.control.add_axes([0.1, 0.20, 0.35, 0.1])
         
        # creates the Buttons in the respectives positions with title and color 
        self.botton_original = Button(ax_original, 'Original Signal', color="#fff700")
        self.botton_hard = Button(ax_hard, 'Hard Clipping', color="#ff0000")
        self.botton_tanh = Button(ax_tanh, 'Soft Clipping (tanh)', color="#ff00d0")
        self.botton_atan = Button(ax_atan, 'Soft Clipping (atan)', color="#51FF00")
        self.botton_algebraic = Button(ax_alg, 'Soft Clipping (algebraico)', color="#00b7ff")
        
        # assigns functions to the buttons when they are clicked
        self.botton_original.on_clicked(self.show_original_signal_graph)
        self.botton_hard.on_clicked(self.show_hard_graph)
        self.botton_tanh.on_clicked(self.show_tanh_graph)
        self.botton_atan.on_clicked(self.show_atan_graph)
        self.botton_algebraic.on_clicked(self.show_algebraic_graph)
    
    def show_original_signal_graph(self, event): 
        original = WavSignal(self.guitar.data, self.guitar.samplerate)
        self.graphs = Graphs(original, self.effects)
        time = original.time()
        self.graphs.graphing('Original Signal', time, original.data, color='cyan')
        frequencies, magnitude = original.fft(original.data, original.samplerate)
        self.graphs.graphing_fft('FFT signal', frequencies, magnitude, color='red')
        frequency, time, spectrum = original.spectrogram(original.data, original.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', time, frequency, spectrum)
    
    def show_hard_graph(self, event):
        
        # takes since prueba_wav.py the effect "Hard" and applies it to the guitar signal data
        signal_hard = self.effects['Hard'].apply(self.guitar.data)
        
        # envolvate the signal in WavSignal
        signal_hard_wav = WavSignal(signal_hard, self.guitar.samplerate)
        # generates the time array for the x-axis of the graph
        time = signal_hard_wav.time()
        # creates an instance of the Graphs class
        self.graphs = Graphs(signal_hard_wav, self.effects)
        # graphs the hard clipping signal and the filtered hard clipping signal
        self.graphs.graphing('hard Clipping', time, signal_hard_wav.data, color= "#ff0000")

        frequencies, magnitude = signal_hard_wav.fft(signal_hard_wav.data, signal_hard_wav.samplerate)
        self.graphs.graphing_fft('FFT HardClippling-Signal', frequencies, magnitude, color='red')
        frequency, time, spectrum = signal_hard_wav.spectrogram(signal_hard_wav.data, signal_hard_wav.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', time, frequency, spectrum)
        
    def show_tanh_graph(self, event):
        # takes since prueba_wav.py the effect "Tanh" and applies it to the guitar signal data
        signal_tanh = self.effects['Tanh'].apply(self.guitar.data)
        
        signal_tanh_wav = WavSignal(signal_tanh, self.guitar.samplerate)
        time = signal_tanh_wav.time()

        self.graphs = Graphs(signal_tanh_wav, self.effects)

        # graphs the tanh clipping signal
        self.graphs.graphing('Tanh Clipping', time, signal_tanh_wav.data, color="#ff00d0")
        frequencies, magnitude = signal_tanh_wav.fft(signal_tanh_wav.data, signal_tanh_wav.samplerate)
        self.graphs.graphing_fft('Tanh Clipping FFT', frequencies, magnitude, color='red')
        frequency, time, spectrum = signal_tanh_wav.spectrogram(signal_tanh_wav.data, signal_tanh_wav.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', time, frequency, spectrum)
        
    def show_atan_graph(self, event):
        # takes since prueba_wav.py the effect "Atan" and applies it to the guitar signal data
        signal_atan = self.effects['Atan'].apply(self.guitar.data)

        signal_atan_wav = WavSignal(signal_atan, self.guitar.samplerate)
        time = signal_atan_wav.time()

        self.graphs = Graphs(signal_atan_wav, self.effects)
        # graphs the atan clipping signal and the filtered atan clipping signal
        self.graphs.graphing('Atan Clipping', time, signal_atan_wav.data, color="#51FF00")
        frequencies, magnitude = signal_atan_wav.fft(signal_atan_wav.data, signal_atan_wav.samplerate)
        self.graphs.graphing_fft('Atan Clipping FFT', frequencies, magnitude, color='red')
        frequency, time, spectrum = signal_atan_wav.spectrogram(signal_atan_wav.data, signal_atan_wav.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', time, frequency, spectrum)

    def show_algebraic_graph(self, event):
        # takes since prueba_wav.py the effect "Algebraic" and applies it to the guitar signal data
        signal_algebraic = self.effects['Algebraic'].apply(self.guitar.data)

        signal_algebraic_wav = WavSignal(signal_algebraic, self.guitar.samplerate)
        time = signal_algebraic_wav.time()
        self.graphs = Graphs(signal_algebraic_wav, self.effects)
        # graphs the algebraic clipping signal and the filtered algebraic clipping signal
        self.graphs.graphing('Algebraic', time, signal_algebraic_wav.data, color="#006086")
        frequencies, magnitude = signal_algebraic_wav.fft(signal_algebraic_wav.data, signal_algebraic_wav.samplerate)
        self.graphs.graphing_fft('Algebraic Clipping FFT', frequencies, magnitude, color='red')
        frequency, time, spectrum = signal_algebraic_wav.spectrogram(signal_algebraic_wav.data, signal_algebraic_wav.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', time, frequency, spectrum)

    # shows the control window with all its components
    def show_control_window(self):
        plt.show(block=True)    
    