from logging import root
import tkinter as tk
import numpy as np
import soundfile as sf
from tkinter import Tk, filedialog
from matplotlib.widgets import Button, Slider
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from graphs import Graphs
from audio_signal import WavSignal, time_x, fft, spectrogram

class Control:
    def __init__(self, effects, style='dark_background'):
        plt.style.use(style) # assigns a style to the plots
        self.effects = effects
        self.use_oversampling = True
       
        # creates principal window "Control" and assings to it rows and columns
        self.control = plt.figure(figsize=(12,4), edgecolor='black') 
        self.gs = GridSpec(2, 1, figure=self.control)
        
        # assings positions to buttoms for add to the control window 
        ax_save = self.control.add_axes([0.02, 0.12, 0.16, 0.08])
        ax_load = self.control.add_axes([0.02, 0.02, 0.16, 0.08])
        ax_original = self.control.add_axes([0.4, 0.80, 0.2, 0.1])
        ax_hard  = self.control.add_axes([0.82, 0.02, 0.16, 0.08])
        ax_tanh  = self.control.add_axes([0.82, 0.11, 0.16, 0.08])
        ax_atan  = self.control.add_axes([0.82, 0.20, 0.16, 0.08])
        ax_alg   = self.control.add_axes([0.82, 0.29, 0.16, 0.08])
        ax_bitcrusher = self.control.add_axes([0.82, 0.38, 0.16, 0.08])  # <-- NUEVO        
        ax_gain = self.control.add_axes([0.25, 0.02, 0.5, 0.03])
        
         
        # creates the Buttons in the respectives positions with title and color 
        self.botton_original = Button(ax_original, 'Original Signal', color="#fff700")
        self.botton_hard = Button(ax_hard, 'Hard Clipping', color="#ff0000")
        self.botton_tanh = Button(ax_tanh, 'Soft Clipping (tanh)', color="#ff00d0")
        self.botton_atan = Button(ax_atan, 'Soft Clipping (atan)', color="#51FF00")
        self.botton_algebraic = Button(ax_alg, 'Soft Clipping (algebraico)', color="#00b7ff")
        self.button_load = Button(ax_load, 'Load .WAV', color="#1e90ff")
        self.button_save = Button(ax_save, "Save Processed WAV", color="#98FB98")
        ax_gain = self.control.add_axes([0.25, 0.02, 0.5, 0.03])
        self.slider_gain = Slider(ax_gain, "PreGain", 1.0, 40.0, valinit=self.effects['PreGain']._gain_db)
        self.button_bitcrusher = Button(ax_bitcrusher, 'BitCrusher', color="#00ffaa")  # <-- NUEVO
        
        # assigns functions to the buttons when they are clicked
        self.botton_original.on_clicked(self.show_original_signal_graph)
        self.botton_hard.on_clicked(self.show_hard_graph)
        self.botton_tanh.on_clicked(self.show_tanh_graph)
        self.botton_atan.on_clicked(self.show_atan_graph)
        self.botton_algebraic.on_clicked(self.show_algebraic_graph)
        self.button_load.on_clicked(self.load_wav)
        self.button_save.on_clicked(self.save_processed_audio)
        self.slider_gain.on_changed(self.update_gain)
        self.button_bitcrusher.on_clicked(self.show_bitcrusher_graph)  # <-- NUEVO
        
    
    def update_gain(self, value):
        self.effects['PreGain'].set_gain(value)
        signal = self.effects['PreGain'].apply(self.guitar.data)

    def show_original_signal_graph(self, event):

        self.graphs = Graphs(self.guitar, self.effects)
        time = time_x(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing('Original Signal', time, self.guitar.data, color='cyan')
        frequencies, magnitude = fft(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing_fft('FFT signal', frequencies, magnitude, color='red')
        F, T, S = spectrogram(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)
        self.update_gain(self.slider_gain.val)

    def show_hard_graph(self, event):
        # takes since prueba_wav.py the effect "Hard" and applies it to the guitar signal data
        signal_hard = self.effects['Hard'].apply(self.guitar.data)
        
    
        # generates the time array for the x-axis of the graph
        time = time_x(signal_hard, self.guitar.samplerate)
        # creates an instance of the Graphs class
        self.graphs = Graphs(self.guitar, self.effects)
        # graphs the hard clipping signal and the filtered hard clipping signal
        self.graphs.graphing('hard Clipping', time, signal_hard, color= "#ff0000")

        frequencies, magnitude = fft(signal_hard, self.guitar.samplerate)
        self.graphs.graphing_fft('FFT HardClippling-Signal', frequencies, magnitude, color='red')
        F, T, S = spectrogram(signal_hard, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)

    def show_tanh_graph(self, event):
        # takes since prueba_wav.py the effect "Tanh" and applies it to the guitar signal data
        signal_tanh = self.effects['Tanh'].apply(self.guitar.data)
        time = time_x(signal_tanh, self.guitar.samplerate)

        self.graphs = Graphs(self.guitar, self.effects)

        # graphs the tanh clipping signal
        self.graphs.graphing('Tanh Clipping', time, signal_tanh, color="#ff00d0")
        frequencies, magnitude = fft(signal_tanh, self.guitar.samplerate)
        self.graphs.graphing_fft('Tanh Clipping FFT', frequencies, magnitude, color='red')
        F, T, S = spectrogram(signal_tanh, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)

    def show_atan_graph(self, event):
        # takes since prueba_wav.py the effect "Atan" and applies it to the guitar signal data
        signal_atan = self.effects['Atan'].apply(self.guitar.data)

        time = time_x(signal_atan, self.guitar.samplerate)

        self.graphs = Graphs(self.guitar, self.effects)
        # graphs the atan clipping signal and the filtered atan clipping signal
        self.graphs.graphing('Atan Clipping', time, signal_atan, color="#51FF00")
        frequencies, magnitude = fft(signal_atan, self.guitar.samplerate)
        self.graphs.graphing_fft('Atan Clipping FFT', frequencies, magnitude, color='red')
        F, T, S = spectrogram(signal_atan, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)

    def show_algebraic_graph(self, event):
        # takes since prueba_wav.py the effect "Algebraic" and applies it to the guitar signal data
        signal_algebraic = self.effects['Algebraic'].apply(self.guitar.data)

        time = time_x(signal_algebraic, self.guitar.samplerate)
        self.graphs = Graphs(self.guitar, self.effects)
        # graphs the algebraic clipping signal and the filtered algebraic clipping signal
        self.graphs.graphing('Algebraic', time, signal_algebraic, color="#006086")
        frequencies, magnitude = fft(signal_algebraic, self.guitar.samplerate)
        self.graphs.graphing_fft('Algebraic Clipping FFT', frequencies, magnitude, color='red')
        F, T, S = spectrogram(signal_algebraic, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)

    def show_bitcrusher_graph(self, event):
        # Aplica el BitCrusher a la señal cargada
        signal_bc = self.effects['BitCrusher'].apply(self.guitar.data)

        time = time_x(signal_bc, self.guitar.samplerate)
        self.graphs = Graphs(self.guitar, self.effects)

        # Señal en el tiempo
        self.graphs.graphing('BitCrusher', time, signal_bc, color="#00ffaa")

        # FFT
        frequencies, magnitude = fft(signal_bc, self.guitar.samplerate)
        self.graphs.graphing_fft('BitCrusher FFT', frequencies, magnitude, color='red')

        # Espectrograma
        F, T, S = spectrogram(signal_bc, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)

        # Para que al guardar use este efecto como "clipping seleccionado"
        self.selected_clipping = 'BitCrusher'


    def load_wav(self, event):
    # Hide root Tk window (we only want the file dialog)
        root = tk.Tk()
        root.withdraw()
    # Ask user to select a WAV file
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")],
            title="Select a WAV audio file"
        )
    # If user cancelled, stop
        if not file_path:
            return
        
    # Read WAV file (data + samplerate)
        signal = WavSignal.archive(file_path)
        signal.normalize()
        
    # Update guitar object with new audio
        self.guitar = signal
        print(f"Loaded WAV: {file_path}")
    
    def process_audio_chain(self):
        signal = self.guitar.data
        samplerate = self.guitar.samplerate
        
        #apply effects chain here if needed
        signal = self.effects['PreGain'].apply(signal)

        if self.use_oversampling:
            signal = self.effects['Oversampler'].upsample(signal)
            
        clip = self.effects[self.selected_clipping]
        signal = clip.apply(signal)
        
        if self.use_oversampling:
            signal = self.effects['Oversampler'].downsample(signal)
        
        self.effects['Filter'].apply(signal)
        self.effects['Delay'].apply(self.guitar)  # usamos el WavSignal original
        signal = self.effects['PostGain'].apply(signal)
        
        return signal
    
    def save_processed_audio(self, event):
        # Generate processed signal
        processed = self.process_audio_chain()

        # Ask user where to save it
        root = tk.Tk()
        root.withdraw()

        save_path = tk.filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
            title="Save processed audio as..."
        )

        # If user cancels, do nothing
        if not save_path:
            return

        # 3. Save WAV
        sf.write(save_path, processed, self.guitar.samplerate)
        print(f"Processed WAV saved at: {save_path}")
    

    # shows the control window with all its components
    def show_control_window(self):
        plt.show(block=True)    
    