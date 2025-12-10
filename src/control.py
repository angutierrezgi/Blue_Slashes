from logging import root
import tkinter as tk
import numpy as np
import soundfile as sf
from tkinter import Tk, filedialog
from matplotlib.widgets import Button, Slider, CheckButtons, RadioButtons
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from graphs import Graphs
from audio_signal import WavSignal, time_x, fft, spectrogram
from distortion import HardClipping

class Control:
    def __init__(self, effects, style='dark_background'):
        plt.style.use(style) # assigns a style to the plots
        self.effects = effects
        self.graphs = None
        self.view_mode = 'chain'
        self.use_oversampling = True
        self.use_delay = True
        self.use_filter = True
        self.selected_clipping = 'Hard'
        self.guitar = None
        
        # creates principal window "Control" and assings to it rows and columns
        self.control = plt.figure(figsize=(12,4), edgecolor='black') 
        self.gs = GridSpec(2, 2, figure=self.control)

        self._create_distortion_panel()
        self._filter_panel_control()
         # mode visualization buttons positions
        ax_mode_solo = self.control.add_axes([0.45, 0.85, 0.12, 0.05])
        ax_mode_chain = self.control.add_axes([0.58, 0.85, 0.12, 0.05])
        
        self.button_mode_solo = Button(ax_mode_solo, 'Solo Effect', color='#4444ff')
        self.button_mode_chain = Button(ax_mode_chain, 'Full Chain', color='#44ff44')
        
        self.button_mode_solo.on_clicked(lambda e: self.set_view_mode('single'))
        self.button_mode_chain.on_clicked(lambda e: self.set_view_mode('chain'))
        
         # assings positions to buttoms for add to the control window
        ax_save = self.control.add_axes([0.02, 0.12, 0.16, 0.08])
        ax_load = self.control.add_axes([0.02, 0.02, 0.16, 0.08])
        ax_original = self.control.add_axes([0.82, 0.47, 0.16, 0.08])
        ax_hard  = self.control.add_axes([0.82, 0.02, 0.16, 0.08])
        ax_tanh  = self.control.add_axes([0.82, 0.11, 0.16, 0.08])
        ax_atan  = self.control.add_axes([0.82, 0.20, 0.16, 0.08])
        ax_alg   = self.control.add_axes([0.82, 0.29, 0.16, 0.08])
        ax_bitcrusher = self.control.add_axes([0.82, 0.38, 0.16, 0.08])      
        ax_gain = self.control.add_axes([0.25, 0.02, 0.5, 0.03])
        
        # creates the Buttons in the respectives positions with title and color 
        self.botton_original = Button(ax_original, 'Original Signal', color="#fff700")
        self.botton_hard = Button(ax_hard, 'Hard Clipping', color="#ff0000")
        self.botton_tanh = Button(ax_tanh, 'Soft Clipping (tanh)', color="#ff00d0")
        self.botton_atan = Button(ax_atan, 'Soft Clipping (atan)', color="#51FF00")
        self.botton_algebraic = Button(ax_alg, 'Soft Clipping (algebraico)', color="#00b7ff")
        self.button_load = Button(ax_load, 'Load .WAV', color="#1e90ff")
        self.button_save = Button(ax_save, "Save Processed WAV", color="#98FB98")
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
        self.button_bitcrusher.on_clicked(self.show_bitcrusher_graph) 
        
    def _create_distortion_panel(self):
        """Control panel for distortion parameters"""
        # Panel area
        distortion_area = self.control.add_subplot(self.gs[0, 0])
        distortion_area.set_axis_off()

        ax_title = self.control.add_axes([0.1, 0.95, 0.25, 0.04])
        ax_title.set_axis_off()
        ax_title.text(0.5, 0.5, 'DISTORTION CONTROL', 
                 ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax_oversample = self.control.add_axes([0.1, 0.90, 0.12, 0.04])
        self.check_oversample = CheckButtons(ax_oversample, ['Oversampling'], 
                            [self.use_oversampling])
        self.check_oversample.on_clicked(self.toggle_oversampling)
        
    #  1. EFFECT SELECTOR
        ax_effect = self.control.add_axes([0.1, 0.80, 0.25, 0.1])
        self.radio_effect = RadioButtons(ax_effect, 
                    ['Hard', 'Tanh', 'Atan', 'Algebraic'])
        self.radio_effect.on_clicked(self._on_effect_changed)
    
    # 2. MODE SELECTOR
        ax_mode = self.control.add_axes([0.1, 0.70, 0.25, 0.1])
        self.radio_mode = RadioButtons(ax_mode,
                    ['Simétrico', 'Asim-Cut', 'Asim-Offset'])
        self.radio_mode.on_clicked(self._on_mode_changed)
    
    # 3. DYNAMIC SLIDERS
    # umbral (always visible)
        ax_umbral = self.control.add_axes([0.1, 0.60, 0.25, 0.03])
        self.slider_umbral = Slider(ax_umbral, "Umbral", 0.01, 1.0, valinit=0.7)
        self.slider_umbral.on_changed(self._on_umbral_changed)
    
    # Variation (initially hidden)
        ax_variation = self.control.add_axes([0.1, 0.55, 0.25, 0.03])
        self.slider_variation = Slider(ax_variation, "Variation", -0.8, 0.8, valinit=0.0)
        self.slider_variation.on_changed(self._on_variation_changed)
        self.slider_variation.ax.set_visible(False)
    
    # Offset (initially hidden)
        ax_offset = self.control.add_axes([0.1, 0.50, 0.25, 0.03])
        self.slider_offset = Slider(ax_offset, "Offset", -0.8, 0.8, valinit=0.0)
        self.slider_offset.on_changed(self._on_offset_changed)
        self.slider_offset.ax.set_visible(False)
    
    # Initialize with default effect
        self._on_effect_changed('Hard')

    def _on_effect_changed(self, effect_name):
        """Cuando cambia el tipo de efecto de distorsión"""
    # 1. Update selected effect
        self.selected_clipping = effect_name
        effect = self.effects[effect_name]
    
    # 2. Load current effect values ​​to sliders
        self.slider_umbral.set_val(effect.get_umbral())
        self.slider_variation.set_val(effect.get_variation())
        self.slider_offset.set_val(effect.get_offset())
    
    # 3. If Hard, adjust variation/offset limits
        if isinstance(effect, HardClipping):
            self._update_hard_limits(effect)
    
    # 4. Update visibility according to current mode
        self._update_slider_visibility()
    
        print(f"Efecto cambiado a: {effect_name}")

    def _on_mode_changed(self, mode_label):
        # when change distorion mode
        # Map labels to internal values
        mode_map = {
        'Simétrico': 'simetric',
        'Asim-Cut': 'asimetric_cut',
        'Asim-Offset': 'asimetric_offset'
        }
    
        mode = mode_map.get(mode_label, 'simetric')
    
    # Update mode in current effect
        effect = self.effects[self.selected_clipping]
        effect.mode = mode
    
    #  update slider visibility
        self._update_slider_visibility()

        print(f"Modo cambiado a: {mode}")

    def _update_slider_visibility(self):
        # Show/hide sliders according to the current mode
        effect = self.effects[self.selected_clipping]
    
        if effect.mode == "simetric":
            self.slider_variation.ax.set_visible(False)
            self.slider_offset.ax.set_visible(False)
        elif effect.mode == "asimetric_cut":
            self.slider_variation.ax.set_visible(True)
            self.slider_offset.ax.set_visible(False)
        elif effect.mode == "asimetric_offset":
            self.slider_variation.ax.set_visible(False)
            self.slider_offset.ax.set_visible(True)
    
        self.control.canvas.draw_idle()

    def _on_umbral_changed(self, value):
        # when change to umbral
        effect = self.effects[self.selected_clipping]
    
        effect.set_umbral(value)
    
        # If Hard, update variation/offset limits
        if isinstance(effect, HardClipping):
            self._update_hard_limits(effect)
    
        # update graph if it exist
        if self.graphs and self.guitar:
            self._refresh_current_graph()

    def _on_variation_changed(self, value):
        # when change to variation
        effect = self.effects[self.selected_clipping]
    
    # Polymorfism: call to HardClipping.set_variation() or Distortion.set_variation()
        effect.set_variation(value)
    
        if self.graphs and self.guitar:
            self._refresh_current_graph()

    def _on_offset_changed(self, value):
        effect = self.effects[self.selected_clipping]
    
        # Polymorfism: call to correct setter 
        effect.set_offset(value)
    
        if self.graphs and self.guitar:
            self._refresh_current_graph()
            
    def _update_hard_limits(self, hard_effect):
        """Updates dinamic limits for HardClipping"""
        umbral = hard_effect.get_umbral()
        limit = umbral * 0.8  # 80% of threshold
    
        # Update variation slider range
        self.slider_variation.valmin = -limit
        self.slider_variation.valmax = limit
    
        # Update range of offset  slider 
        self.slider_offset.valmin = -limit
        self.slider_offset.valmax = limit
    
    # If the current value is outside the new range, adjust it
        current_var = self.slider_variation.val
        if current_var < -limit or current_var > limit:
            self.slider_variation.set_val(max(-limit, min(limit, current_var)))
    
        current_off = self.slider_offset.val
        if current_off < -limit or current_off > limit:
            self.slider_offset.set_val(max(-limit, min(limit, current_off)))

    def _filter_panel_control(self):
        pass
    
    def _refresh_current_graph(self):
        # update Graphs con actual configuration
        if not self.guitar or not self.graphs:
            return
    
        # Apply effect according to the mode
        if self.view_mode == 'single':
            signal = self._apply_effect_solo(self.selected_clipping)
            title = f'{self.selected_clipping}'
        else:  # 'chain'
            signal = self._apply_full_chain()
            title = f'Chain: {self.selected_clipping}'
    
        # update Graphs
        time = time_x(signal, self.guitar.samplerate)
        self.graphs.graphing(title, time, signal, self._get_effect_color())
    
        frequencies, magnitude = fft(signal, self.guitar.samplerate)
        self.graphs.graphing_fft(f'FFT - {title}', frequencies, magnitude, "red")
    
        F, T, S = spectrogram(signal, self.guitar.samplerate)
        self.graphs.graphing_spectrogram(f'Spectrogram - {title}', T, F, S)

    def set_view_mode(self, mode):
        self.view_mode = mode
        print(f"View mode: {mode}")
    
    def toggle_oversampling(self, label):
        """Callback for toggle of oversampling"""
        self.use_oversampling = not self.use_oversampling
        status = "ON" if self.use_oversampling else "OFF"
        print(f"Oversampling: {status}")
    
        # update graph if it exists
        if self.graphs and self.guitar:
            self._refresh_current_graph()
        
    def _apply_effect_solo(self, effect_name):
        if not self.guitar or effect_name not in self.effects:
            return self.guitar.data if self.guitar else None
        
        signal = self.guitar.data.copy()
        
        signal = self.effects['PreGain'].apply(signal)
        # Apply the effect to the guitar signal
        signal = self.effects[effect_name].apply(signal)
        return signal
        
    def _apply_full_chain(self):
        if not self.guitar:
            return None
            
        signal = self.guitar.data.copy()

        signal = self.effects['PreGain'].apply(signal)
            
        if self.use_oversampling and 'Oversampler' in self.effects:
            signal = self.effects['Oversampler'].upsample(signal)
        if self.selected_clipping in self.effects:
            signal = self.effects[self.selected_clipping].apply(signal)
        if self.use_oversampling and 'Oversampler' in self.effects:
            signal = self.effects['Oversampler'].downsample(signal)  
        
        if self.use_filter and 'Filter' in self.effects:
            signal = self.effects['Filter'].apply(signal)
            
        if self.use_delay and 'Delay' in self.effects:
            signal = self.effects['Delay'].apply(signal, self.guitar.samplerate)
            
        signal = self.effects['PostGain'].apply(signal)
            
        return signal
        
    def show_current_settings_graph(self, event):
            
        if not self.guitar:
            return print("No guitar signal loaded.")

        if self.view_mode == 'single':
            signal = self._apply_effect_solo(self.selected_clipping)
            title = f'{self.selected_clipping} Only'
            
        elif self.view_mode == "chain":
            signal = self._apply_full_chain()
            title = f'Full Chain: {self.selected_clipping}'
        
        else: 
            signal = self.guitar
            title = 'Original signal'
                            
        if not self.graphs:
            self.graphs = Graphs(self.guitar, self.effects)
            
        time = time_x(signal, self.guitar.samplerate)

        self.graphs.graphing(title, time, signal,"#ff0000" )
        # FFT
        frequencies, magnitude = fft(signal, self.guitar.samplerate)
        self.graphs.graphing_fft(f'FFT - {title}', frequencies, magnitude, "red")
            
        # spectogram
        F, T, S = spectrogram(signal, self.guitar.samplerate)
        self.graphs.graphing_spectrogram(f'Spectrogram - {title}', T, F, S)
            
    def update_gain(self, value):
        """Para el slider de gain"""
        self.effects['PreGain'].set_gain(value)
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def show_original_signal_graph(self, event):
        
        if not self.graphs:
            self.graphs = Graphs(self.guitar, self.effects)
        
        time = time_x(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing('Original Signal', time, self.guitar.data, color='cyan')
        frequencies, magnitude = fft(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing_fft('FFT signal', frequencies, magnitude, color='red')
        F, T, S = spectrogram(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)
        self.update_gain(self.slider_gain.val)

    def show_hard_graph(self, event):
        self.selected_clipping = 'Hard'
        self.show_current_settings_graph(event)
        
    def show_tanh_graph(self, event):
        self.selected_clipping = 'Tanh'
        self.show_current_settings_graph(event)

    def show_atan_graph(self, event):
        self.selected_clipping = 'Atan'
        self.show_current_settings_graph(event)
    
    def show_algebraic_graph(self, event):
        self.selected_clipping = 'Algebraic'
        self.show_current_settings_graph(event)
        
    def show_bitcrusher_graph(self, event):
        self.selected_clipping = 'BitCrusher'
        self.show_current_settings_graph(event)

    def _get_effect_color(self):
        """Returns color according to the effect selected"""
        colors = {
            'Hard': '#ff0000',
            'Tanh': '#ff00d0', 
            'Atan': '#51FF00',
            'Algebraic': '#00b7ff',
            'BitCrusher': '#00ffaa',
            'Original': 'cyan'
        }
        return colors.get(self.selected_clipping, '#ffffff')
    
    def load_wav(self, event):
        
        root = get_tk_root() 
    # Ask user to select a WAV file
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")],
            title="Select a WAV audio file",
            parent = root
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
     
    def save_processed_audio(self, event):
        # Generate processed signal
        processed = self._apply_full_chain()
        root = get_tk_root() 
        # Ask user where to save it
        save_path = tk.filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
            title="Save processed audio as...",
            parent= root
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
        

_tk_root_instance = None  # Globar variable for Singleton

def get_tk_root():
    """Devuelve una única instancia de Tk() para toda la aplicación"""
    global _tk_root_instance
    if _tk_root_instance is None:
        _tk_root_instance = tk.Tk()
        _tk_root_instance.withdraw()
        # Configure to survive graph shutdowns
        _tk_root_instance.attributes('-topmost', False)
    return _tk_root_instance  
    