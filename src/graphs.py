import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

class Graphs:
    def __init__(self, guitar_signal, style='dark_background'):
        plt.style.use(style)
        self.guitar_signal = guitar_signal # signal that will be graphed
        self.window = plt.figure(figsize=(12,12), edgecolor='black') #creates a window
        self.grid = GridSpec(3, 1, figure=self.window) # assigns to window 2 rows and 1 column
        
        
        
    def graphing(self, title, ejex, ejey, color='cyan'):
        # creates a subplot in the first row
        clipping_signal = self.window.add_subplot(self.grid[0,:])
        # plots the signal in the subplot, with specified color and line width
        clipping_signal.plot(ejex, ejey, color=color, linewidth=0.2)
        # sets the title and labels of the subplot
        clipping_signal.set_title(title)
        clipping_signal.set_xlabel('Time (s)')
        clipping_signal.set_ylabel('Amplitude')
        # enables grid with specified transparency
        clipping_signal.grid(True, alpha=0.3)
        # displays the plot without blocking the execution
        plt.show(block=False)  
        
    def graphing_fft(self, title, ejex, ejey, color='cyan'): 
        # creates a subplot in the second row   
        filtered_signal = self.window.add_subplot(self.grid[1, :])
        # plots the filtered signal in the subplot, with specified color and line width
        filtered_signal.plot(ejex, ejey, color=color, linewidth=0.2)
        filtered_signal.set_title(title)
        filtered_signal.set_xlabel('Frequency (Hz)')
        filtered_signal.set_ylabel('Magnitude')
        filtered_signal.grid(True, alpha=0.3)
        # displays the plot without blocking the execution
        plt.show(block=False)    
           
    def graphing_spectrogram(self, title, time, frequency, spectrum):
        spectrum_signal = self.window.add_subplot(self.grid[2,:])
        spectrum_signal.pcolormesh(time, frequency, spectrum, shading='gouraud', cmap='inferno')
        spectrum_signal.set_xlabel('Time (s)')
        spectrum_signal.set_ylabel('Frequency (Hz)')
        spectrum_signal.set_ylim(0, 4000)

        spectrum_signal.colorbar(spectrum_signal.pcolormesh(time, frequency, spectrum, shading='gouraud', cmap='inferno'), ax=spectrum_signal)
        plt.show(block=False)
