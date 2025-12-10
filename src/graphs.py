import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
from audio_signal import time_x, fft, spectrogram


class Graphs:
    def __init__(self, signal, effects, style='dark_background'):
        plt.style.use(style)
        self.signal = signal # signal that will be graphed   
        self.effects = effects
        
        self.window = plt.figure(figsize=(12,12), edgecolor='black') #creates a window
        self.grid = GridSpec(3, 1, figure=self.window) # assigns to window 2 rows and 1 column
        self.time_signal = self.window.add_subplot(self.grid[0,:])
        self.fft_signal = self.window.add_subplot(self.grid[1, :])
        self.spectrum_signal = self.window.add_subplot(self.grid[2,:]) # creates a subplot in the third row
        show_filtered = self.window.add_axes([0.8, 0.92, 0.1, 0.05]) # button for show filtered signal
        self.button_show_filtered = Button(show_filtered, 'Show Filtered', color="#00ffcc") # creates the button
        # links the button to the function that shows the filtered signal
        self.button_show_filtered.on_clicked(self.show_filtered_graph)
    
    def graphing(self, title, ejex, ejey, color='cyan'):
        # flattens the input arrays to ensure they are 1D
        x = np.asarray(ejex).ravel()
        y = np.asarray(ejey).ravel()

        self.time_signal.clear()
        # plots the signal in the subplot, with specified color and line width
        self.time_signal.plot(x, y, color=color, linewidth=0.2)
        # sets the title and labels of the subplot
        self.time_signal.set_title(title)
        self.time_signal.set_xlabel('Time (s)')
        self.time_signal.set_ylabel('Amplitude')
        # enables grid with specified transparency
        self.time_signal.grid(True, alpha=0.3)
        # displays the plot without blocking the execution
        plt.show(block=False)  
        
    def graphing_fft(self, title, ejex, ejey, color='cyan'): 
        f = np.asarray(ejex).ravel()
        m = np.asarray(ejey).ravel()
        
        self.fft_signal.clear()
        # plots the filtered signal in the subplot, with specified color and line width
        self.fft_signal.plot(f, m, color=color, linewidth=0.2)
        self.fft_signal.set_title(title)
        self.fft_signal.set_xlabel('Frequency (Hz)')
        self.fft_signal.set_ylabel('Magnitude')
        self.fft_signal.grid(True, alpha=0.3)
        # displays the plot without blocking the execution
        self.window.canvas.draw_idle()
           
    def graphing_spectrogram(self, title, time, frequency, spectrum):
        t = np.asarray(time).ravel()
        f = np.asarray(frequency).ravel()
        S = np.asarray(spectrum)

        self.spectrum_signal.clear()
        self.spectrum_signal.set_title(title)
    
        #  Delete old axle
        self.spectrum_signal.remove()
        
        # Create NEW axis in the same position
        self.spectrum_signal = self.window.add_subplot(self.grid[2, :])
        self.spectrum_signal.set_title(title) 

        # plots the spectrogram using pcolormesh with specified colormap
        mesh =self.spectrum_signal.pcolormesh(t, f, S, shading='gouraud', cmap='inferno')
        self.spectrum_signal.set_xlabel('Time (s)')
        self.spectrum_signal.set_ylabel('Frequency (Hz)')
        self.spectrum_signal.set_ylim(0, 4000) # limits y-axis to 4000 Hz
         # adds a colorbar to indicate the intensity of the spectrogram
        current_colorbar = self.window.colorbar(mesh, ax=self.spectrum_signal)
       
    
        self.window.canvas.draw_idle()

    def show_filtered_graph(self, event):
        x = np.asarray(self.signal.data, dtype=float)
        signal_filtered = np.array(self.effects['Filter'].apply(x), dtype=float) # applies the filter effect to vector-data
        times = time_x(signal_filtered, self.signal.samplerate) # generates time vector for x-axis
        # graphs the filtered signal
        self.graphing('Filtered Signal', times, signal_filtered, color= "#ff0000")
        # applies FFT and spectrogram to the filtered signal and graphs them
        frequencies, magnitude = fft(signal_filtered, self.signal.samplerate)
        self.graphing_fft('FFT filtered Signal', frequencies, magnitude, color ="#e05454")
        frequency, time, spectrum = spectrogram(signal_filtered, self.signal.samplerate)
        self.graphing_spectrogram('Spectrogram Filtered Signal', time, frequency, spectrum)
   