import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import soundfile as sf
from scipy.signal import butter, lfilter
from matplotlib.widgets import Button

class Control:
    def __init__(self, guitar, effects, style='dark_background'):
        plt.style.use(style)
        self.guitar = guitar
        self.effects = effects
    
        self.control = plt.figure(figsize=(12,4), edgecolor='black')
        self.gs = GridSpec(2, 1, figure=self.control)
        
        ax_hard = self.control.add_axes([0.1, 0.05, 0.35, 0.1])
        ax_tanh = self.control.add_axes([0.6, 0.20, 0.35, 0.1])
        ax_atan = self.control.add_axes([0.6, 0.05, 0.35, 0.1])
        ax_alg  = self.control.add_axes([0.1, 0.20, 0.35, 0.1])
         
        self.botton_hard = Button(ax_hard, 'Hard Clipping', color="#ff0000")
        self.botton_tanh = Button(ax_tanh, 'Soft Clipping (tanh)', color="#ff00d0")
        self.botton_atan = Button(ax_atan, 'Soft Clipping (atan)', color="#51FF00")
        self.botton_algebraic = Button(ax_alg, 'Soft Clipping (algebraico)', color="#00b7ff")
        
        self.botton_hard.on_clicked(self.show_hard_graph)
        self.botton_tanh.on_clicked(self.show_tanh_graph)
        self.botton_atan.on_clicked(self.show_atan_graph)
        self.botton_algebraic.on_clicked(self.show_algebraic_graph)
    
   
    
    
    def show_hard_graph(self, event):
        signal_hard = self.effects['Hard'].apply(self.guitar.data)
        time = self.guitar.time()
        signal_hard_filtered = self.effects['Filter'].apply(signal_hard)

        self.graphs = Graphs(self.guitar)
        
        self.graphs.graphing('hard Clipping', time, signal_hard, color= "#ff0000")
        self.graphs.graphing_filtered('filtered hard Clipping', time, signal_hard_filtered, color="#ff8c00")
        
    
    def show_tanh_graph(self, event):
        signal_tanh = self.effects['Tanh'].apply(self.guitar.data)
        time = self.guitar.time()
        filtered_signal_tanh = self.effects['Filter'].apply(signal_tanh)
        self.graphs = Graphs(self.guitar)
        
        self.graphs.graphing('Tanh Clipping', time, signal_tanh, color="#ff00d0")
        self.graphs.graphing_filtered('filtered Tanh Clipping', time, filtered_signal_tanh, color="#ff69b4")
        
    def show_atan_graph(self, event):
        signal_tanh = self.effects['Atan'].apply(self.guitar.data)
        time = self.guitar.time()
        signal_tanh_filtered = self.effects['Filter'].apply(signal_tanh)

        self.graphs = Graphs(self.guitar)
        self.graphs.graphing('Atan Clipping', time, signal_tanh, color="#51FF00")
        self.graphs.graphing_filtered('Atan Clipping', time, signal_tanh_filtered, color="#06FF76")
        
    def show_algebraic_graph(self, event):
        signal_algebraic = self.effects['Algebraic'].apply(self.guitar.data)
        time = self.guitar.time()
        signal_algebraic_filtered = self.effects['Filter'].apply(signal_algebraic)

        self.graphs = Graphs(self.guitar)
        self.graphs.graphing('Algebraic', time, signal_algebraic, color="#006086")   
        self.graphs.graphing_filtered('filtered Algebraic', time, signal_algebraic_filtered, color="#00ffcc")
    
    def original_signal_graph(self, ejex, ejey): 
        ax_normal = self.control.add_subplot(self.gs[0,:])
        ax_normal.plot(ejex, ejey, color='cyan', linewidth=0.3)
        
        ax_normal.set_title('señal de audio -guitarra')
        ax_normal.set_xlabel('Tiempo (s)')
        ax_normal.set_ylabel('Amplitud')
        ax_normal.grid(True, alpha=0.3)
        return ax_normal
          
    def show_control_window(self):
        plt.show(block=True)    
        
class Graphs:
    def __init__(self, guitar_signal, style='dark_background'):
        plt.style.use(style)
        self.guitar_signal = guitar_signal
        self.window = plt.figure(figsize=(12,4), edgecolor='black')
        self.grid = GridSpec(2, 1, figure=self.window)
        
        
        
    def graphing(self, title, ejex, ejey, color='cyan'):
        
        clipping_signal = self.window.add_subplot(self.grid[0,:])
        clipping_signal.plot(ejex, ejey, color=color, linewidth=0.2)
        clipping_signal.set_title(title)
        clipping_signal.set_xlabel('Time (s)')
        clipping_signal.set_ylabel('Amplitude')
        clipping_signal.grid(True, alpha=0.3)
        plt.show(block=False)  
        
    def graphing_filtered(self, title, ejex, ejey, color='cyan'):    
        filtered_signal = self.window.add_subplot(self.grid[1, :])
        filtered_signal.plot(ejex, ejey, color=color, linewidth = 0.2)
        filtered_signal.set_title(title)
        filtered_signal.set_xlabel('Time (s)')
        filtered_signal.set_ylabel('Amplitude')
        filtered_signal.grid(True, alpha=0.3)
        plt.show(block=False)       
        