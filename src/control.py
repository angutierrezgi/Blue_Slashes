from logging import root
from tabnanny import check
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
        self.use_bitcrusher = False
        self.use_oversampling = True
        self.use_distortion = False
        self.use_reverb = False
        self.use_delay = False
        self.use_filter = False
        self.selected_clipping = 'Hard'
        self.guitar = None
        
        # creates principal window "Control" and assings to it rows and columns
        self.control = plt.figure(figsize=(12,4), edgecolor='black') 
        try:
            import matplotlib.image as mpimg
            # Add background image
            bg_ax = self.control.add_axes([0, 0, 1, 1], zorder=-1)
            bg_ax.set_axis_off()
            
            # Charge and display the background image
            img = mpimg.imread(r"C:\Users\s4mue\OneDrive\Escritorio\imagen fondo.png")  
            bg_ax.imshow(img, extent=[0, 1, 0, 1], aspect='auto', alpha=0.2)
        except:
            self.control.patch.set_facecolor('#1a1a2e')
        self.gs = GridSpec(3, 3, figure=self.control)

        self._create_bitcrusher_panel()  
        self._create_reverb_panel()
        self._create_delay_panel()
        self._create_distortion_panel()
        self._filter_panel_control()
        
         # mode visualization buttons positions
        ax_mode_solo = self.control.add_axes([0.018, 0.22, 0.12, 0.05])
        ax_mode_chain = self.control.add_axes([0.018, 0.28, 0.12, 0.05])
        
        self.button_mode_solo = Button(ax_mode_solo, 'Solo Effect', color='#4444ff')
        self.button_mode_chain = Button(ax_mode_chain, 'Full Chain', color='#44ff44')
        
        self.button_mode_solo.on_clicked(lambda e: self.set_view_mode('single'))
        self.button_mode_chain.on_clicked(lambda e: self.set_view_mode('chain'))
        
         # assings positions to buttoms for add to the control window
        ax_save = self.control.add_axes([0.018, 0.12, 0.12, 0.08])
        ax_load = self.control.add_axes([0.018, 0.02, 0.12, 0.08])
        ax_original = self.control.add_axes([0.018, 0.42, 0.12, 0.08])
        ax_bitcrusher = self.control.add_axes([0.54, 0.50, 0.08, 0.04])      
        ax_gain = self.control.add_axes([0.20, 0.02, 0.25, 0.03])
        ax_post_gain = self.control.add_axes([0.20, 0.06, 0.25, 0.03])
        # creates the Buttons in the respectives positions with title and color 
        self.botton_original = Button(ax_original, 'Original Signal', color="#04289f")
        self.button_load = Button(ax_load, 'Load .WAV', color="#1e90ff")
        self.button_save = Button(ax_save, "Save Processed WAV", color="#000000")
        self.slider_gain = Slider(ax_gain, "PreGain", 1.0, 40.0, valinit=self.effects['PreGain']._gain_db)
        self.slider_post_gain = Slider(ax_post_gain, "PostGain", -20.0, 20.0, valinit=self.effects['PostGain']._post_gain_db)
        self.button_bitcrusher = Button(ax_bitcrusher, 'Graph', color="#036746")  # <-- NUEVO
        
        # assigns functions to the buttons when they are clicked
        self.botton_original.on_clicked(self.show_original_signal_graph)
        self.button_load.on_clicked(self.load_wav)
        self.button_save.on_clicked(self.save_processed_audio)
        self.slider_gain.on_changed(self.update_gain)
        self.slider_post_gain.on_changed(self.update_post_gain)
        self.button_bitcrusher.on_clicked(self.show_bitcrusher_graph) 
    
    def set_view_mode(self, mode):
        self.view_mode = mode
        print(f"View mode: {mode}")
    
    def update_gain(self, value):
        """for slider gain change"""
        self.effects['PreGain'].set_gain(value)
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def update_post_gain(self, value):
        """for slider post-gain change"""
        self.effects['PostGain'].set_gain(value)
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def _filter_panel_control(self):
        """Control panel for filter"""
        filter_area = self.control.add_subplot(self.gs[0, 2])
        filter_area.set_axis_off()
        ax_title = self.control.add_axes([0.7, 0.95, 0.25, 0.04])
        ax_title.set_axis_off()
        ax_title.text(0.5, 0.5, 'FILTER CONTROL', 
                 ha='center', va='center', fontweight='bold', fontsize=10)
        
        # toggle for filter usage
        ax_filter_toggle = self.control.add_axes([0.7, 0.90, 0.12, 0.04])
        self.check_filter = CheckButtons(ax_filter_toggle, ['Filter ON'], 
                                     [getattr(self, 'use_filter', True)])
        self.check_filter.on_clicked(self.toggle_filter)
        self._style_checkbutton(self.check_filter, 'Filter')
        
        
        # slider for low frequency
        ax_low = self.control.add_axes([0.7, 0.84, 0.25, 0.03])
        filter_effect = self.effects.get('Filter')
        if filter_effect:
            initial_low = filter_effect.low_frequency
        else:
            initial_low = 400.0
    
        self.slider_low = Slider(ax_low, "Low Cut (Hz)", 20.0, 2000.0, 
                             valinit=initial_low, valfmt='%0.0f')
        self.slider_low.on_changed(self._on_low_freq_changed)
        
        # slider for high frequency
        
        ax_high = self.control.add_axes([0.7, 0.79, 0.25, 0.03])
    
        if filter_effect:
            initial_high = filter_effect.high_frequency
        else:
            initial_high = 4000.0
    
        self.slider_high = Slider(ax_high, "High Cut (Hz)", 1000.0, 8000.0, 
                              valinit=initial_high, valfmt='%0.0f')
        self.slider_high.on_changed(self._on_high_freq_changed)
        
        # slider for order
        ax_order = self.control.add_axes([0.7, 0.74, 0.25, 0.03])
    
        if filter_effect:
            initial_order = filter_effect.order
        else:
            initial_order = 2
    
        self.slider_order = Slider(ax_order, "Order", 1, 8, 
                        valinit=initial_order, valstep=1, valfmt='%0.0f')
        self.slider_order.on_changed(self._on_filter_order_changed)
    
    def toggle_filter(self, label):
        
        # synchronize state
        new_state = self.check_filter.get_status()[0]
        self.use_filter = new_state  
    
        print(f"Filter: {'ON' if self.use_filter else 'OFF'}")
        self._style_checkbutton(self.check_filter, 'Filter')

        self.control.canvas.draw_idle()
    
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def _on_low_freq_changed(self, value):
        """change low cutoff frequency"""
        if 'Filter' in self.effects:
            # Ensure low < high
            current_high = self.effects['Filter'].high_frequency
            new_high = max(value + 100, current_high)  # Maintain at least 100Hz separation

            self.effects['Filter'].low_frequency = value
            self.slider_high.set_val(new_high)  # Update slider if adjusted

            print(f"Filter low frequency: {value:.0f} Hz")


            # Update graph if there is a signal
            if self.graphs and self.guitar and getattr(self, 'use_filter', True):
                self._refresh_current_graph()
                
                
    def _on_high_freq_changed(self, value):
        """when changes high cutoff frequency"""
        if 'Filter' in self.effects:
            # Ensure high > low
            current_low = self.effects['Filter'].low_frequency
            new_high = max(value, current_low + 100)  # Maintain at least 100Hz separation

            self.effects['Filter'].high_frequency = new_high
            self.slider_high.set_val(new_high)  # Update slider if adjusted

            print(f"Filter high frequency: {new_high:.0f} Hz")


            # Update graph if there is a signal
            if self.graphs and self.guitar and getattr(self, 'use_filter', True):
                self._refresh_current_graph()
           
    def _on_filter_order_changed(self, value):
        """change filter order"""
        if 'Filter' in self.effects:
            self.effects['Filter'].order = int(value)
            print(f"Filter order: {int(value)}")

        
        # Update graph if there is a signal
        if self.graphs and self.guitar and getattr(self, 'use_filter', True):
            self._refresh_current_graph()

    def _create_reverb_panel(self):
        
        # Panel Area
        reverb_area = self.control.add_subplot(self.gs[0, 2])
        reverb_area.set_axis_off()
    
        #  Title
        ax_title = self.control.add_axes([0.7, 0.55, 0.25, 0.04])
        ax_title.set_axis_off()
        ax_title.text(0.5, 0.5, 'REVERB', 
                 ha='center', va='center', fontweight='bold', fontsize=10)
    
        # TOGGLE ON/OFF 
        ax_toggle = self.control.add_axes([0.7, 0.50, 0.12, 0.04])
        self.check_reverb = CheckButtons(ax_toggle, ['ON'], 
                                     [getattr(self, 'use_reverb', False)])
        self.check_reverb.on_clicked(self.toggle_reverb)
        self._style_checkbutton(self.check_reverb, 'Reverb')

        # RADIOBUTTONS PRESETS 
        ax_presets = self.control.add_axes([0.7, 0.38, 0.25, 0.11])  
        self.radio_reverb = RadioButtons(ax_presets, 
                                    ['Room', 'Hall', 'Cathedral', 'Canyon', 'Manual'],
                                    active=0)  
        self.radio_reverb.on_clicked(self._on_reverb_preset_changed)

         # Sliders para modo manual (inicialmente ocultos/desactivados)
        ax_slider_wet = self.control.add_axes([0.7, 0.30, 0.25, 0.02])
        self.slider_wet = Slider(ax_slider_wet, 'Wet', 0.0, 1.0, valinit=0.4)
        self.slider_wet.on_changed(self._on_manual_reverb_changed)
    
        ax_slider_delay = self.control.add_axes([0.7, 0.26, 0.25, 0.02])
        self.slider_delay = Slider(ax_slider_delay, 'Pre Delay', 0.0, 0.3, valinit=0.02)
        self.slider_delay.on_changed(self._on_manual_reverb_changed)
    
        ax_slider_decay = self.control.add_axes([0.7, 0.22, 0.25, 0.02])
        self.slider_decay = Slider(ax_slider_decay, 'Decay Time', 0.005, 0.15, valinit=0.01)
        self.slider_decay.on_changed(self._on_manual_reverb_changed)
    
        ax_slider_repeats = self.control.add_axes([0.7, 0.18, 0.25, 0.02])
        self.slider_repeats = Slider(ax_slider_repeats, 'Repeats', 1, 30, valinit=8, valstep=1)
        self.slider_repeats.on_changed(self._on_manual_reverb_changed)
    
        ax_slider_dampening = self.control.add_axes([0.7, 0.14, 0.25, 0.02])
        self.slider_dampening = Slider(ax_slider_dampening, 'Dampening', 0.1, 1.0, valinit=0.5)
        self.slider_dampening.on_changed(self._on_manual_reverb_changed)
    
        self._toggle_manual_sliders(visible=True)
        
    def _on_reverb_preset_changed(self, preset_label):
        if 'Reverb' not in self.effects:
            return

        # show/hide manual sliders
        if preset_label == 'Manual':
            self._toggle_manual_sliders(visible=True)

            # If we are in manual mode, load current values to sliders
            reverb_effect = self.effects['Reverb']
            self.slider_wet.set_val(reverb_effect.get_wet())
            self.slider_delay.set_val(reverb_effect.get_pre_delay())
            self.slider_decay.set_val(reverb_effect.get_seconds())
            self.slider_repeats.set_val(reverb_effect.get_repeats())
            self.slider_dampening.set_val(reverb_effect.get_dampening())
        else:
            self._toggle_manual_sliders(visible=False)
        
            # Map label to internal name
            preset_map = {
                'Room': 'room',
                'Hall': 'hall', 
                'Cathedral': 'cathedral',
                'Canyon': 'canyon'
            }
    
            preset_name = preset_map.get(preset_label, 'room')
    
            # Apply preset
            self.effects['Reverb'].ambient = preset_name
    

        # update graph if there is a signal
        if getattr(self, 'use_reverb', False) and self.graphs and self.guitar:
            self._refresh_current_graph()
        self.control.canvas.draw_idle()
    
    def _on_manual_reverb_changed(self, val):
        if 'Reverb' not in self.effects or self.radio_reverb.value_selected != 'Manual':
            return
    
        reverb_effect = self.effects['Reverb']
    
        # update reverb parameters
        reverb_effect.set_wet(self.slider_wet.val)
        reverb_effect.set_pre_delay(self.slider_delay.val)
        reverb_effect.set_seconds(self.slider_decay.val)
        reverb_effect.set_repeats(int(self.slider_repeats.val))
        reverb_effect.set_dampening(self.slider_dampening.val)

        # Force manual mode
        reverb_effect._ambient = "manual"
    
        # update graph if there is a signal
        if getattr(self, 'use_reverb', False) and self.graphs and self.guitar:
            self._refresh_current_graph()

    def _toggle_manual_sliders(self, visible=True):
        """Show or hide manual reverb sliders"""
        sliders = [
            self.slider_wet, self.slider_delay, self.slider_decay,
            self.slider_repeats, self.slider_dampening
        ]
    
        for slider in sliders:
            
            slider.ax.set_visible(visible)

        
    
            if hasattr(slider, 'vline'):
                slider.vline.set_visible(visible)
            if hasattr(slider, 'line'):
                slider.vline.set_visible(visible)
            if hasattr(slider, 'poly'):
                slider.poly.set_visible(visible)
            if hasattr(slider, 'valtext'):
                slider.valtext.set_visible(visible)
        
            if hasattr(slider, 'label'):
                slider.label.set_visible(visible)
    
        self.control.canvas.draw_idle()
    
    def toggle_reverb(self, label):
        # synchronize state
        new_state = self.check_reverb.get_status()[0]
        self.use_reverb = new_state  
    
        print(f"Reverb: {'ON' if self.use_reverb else 'OFF'}")
        self._style_checkbutton(self.check_reverb, 'Reverb')

        self.control.canvas.draw_idle()
    
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def _create_delay_panel(self):
        """Control panel for delay parameters"""
        delay_area = self.control.add_subplot(self.gs[0, 1])
        delay_area.set_axis_off()

        ax_title = self.control.add_axes([0.35, 0.95, 0.24, 0.04])
        ax_title.set_axis_off()
        ax_title.text(0.5, 0.5, 'DELAY CONTROL', 
                 ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax_delay_toggle = self.control.add_axes([0.38, 0.90, 0.15, 0.04])
        self.check_delay = CheckButtons(ax_delay_toggle, ['Delay'], 
                            [getattr(self, 'use_delay', True)])
        self.check_delay.on_clicked(self.toggle_delay)
        self._style_checkbutton(self.check_delay, 'Delay')
        
        
        # SLIDER DAMPENING 
        ax_dampening = self.control.add_axes([0.38, 0.85, 0.20, 0.03])
    
        # get initial value from effect if exists
        delay_effect = self.effects.get('Delay')
        if delay_effect:
            initial_damp = delay_effect._dampening  # use internal attribute
        else:
            initial_damp = 0.6

        # LLimits: 0.0 (no echo) to 0.95 (very long echoes)
        # More than 0.95 can cause infinite feedback
        self.slider_dampening = Slider(ax_dampening, "Feedback", 0.0, 0.95, 
                                   valinit=initial_damp, valfmt='%0.2f')
        self.slider_dampening.on_changed(self._on_dampening_changed)
    
        # SLIDER SECONDS 
        ax_seconds = self.control.add_axes([0.38, 0.77, 0.20, 0.03])
    
        if delay_effect:
            initial_sec = delay_effect._seconds  # use internal attribute
        else:
            initial_sec = 0.5

        # LLimits: 0.05s (very fast) to 2.0s (very slow)

        self.slider_seconds = Slider(ax_seconds, "Time (s)", 0.05, 2.0, 
                                 valinit=initial_sec, valfmt='%0.2f')
        self.slider_seconds.on_changed(self._on_seconds_changed)
    
        # SLIDER REPEATS
        ax_repeats = self.control.add_axes([0.38, 0.70, 0.20, 0.03])
    
        if delay_effect:
            initial_rep = delay_effect._repeats  # use internal attribute
        else:
            initial_rep = 3

        # More than 10 can be too much for normal audio
        self.slider_repeats = Slider(ax_repeats, "Repeats", 1, 10, 
                                 valinit=initial_rep, valstep=1, valfmt='%0.0f')
        self.slider_repeats.on_changed(self._on_repeats_changed)
    
    def toggle_delay(self, label):
    
       # synchronize state
        new_state = self.check_delay.get_status()[0]
        self.use_delay = new_state  
    
        print(f"Delay: {'ON' if self.use_delay else 'OFF'}")
        self._style_checkbutton(self.check_delay, 'Delay')

        self.control.canvas.draw_idle()
    
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def _on_dampening_changed(self, value):
        """when changes dampening value"""
        if 'Delay' in self.effects:
            self.effects['Delay'].dampening = value

            if getattr(self, 'use_delay', True) and self.graphs and self.guitar:
                self._refresh_current_graph()
    
    def _on_seconds_changed(self, value):
        """when changes delay time"""
        if 'Delay' in self.effects:
            self.effects['Delay'].seconds = value
        
        
            if getattr(self, 'use_delay', True) and self.graphs and self.guitar:
                self._refresh_current_graph()
    
    def _on_repeats_changed(self, value):
        """when changes number of repeats"""
        if 'Delay' in self.effects:
            self.effects['Delay'].repeats = int(value)
        
            if getattr(self, 'use_delay', True) and self.graphs and self.guitar:
                self._refresh_current_graph()
    
    def _create_bitcrusher_panel(self):
        """panel control for bitcrusher effect"""
        crusher_area = self.control.add_subplot(self.gs[1, 1]) 
        crusher_area.set_axis_off()
    
        # Title
        ax_title = self.control.add_axes([0.35, 0.55, 0.24, 0.04])
        ax_title.set_axis_off()
        ax_title.text(0.5, 0.5, 'BITCRUSHER', 
                 ha='center', va='center', fontweight='bold', fontsize=10)
    
        # TOGGLE ON/OFF 
        ax_crusher_toggle = self.control.add_axes([0.38, 0.50, 0.16, 0.04])
        self.check_crusher = CheckButtons(ax_crusher_toggle, ['ON'], 
                                      [getattr(self, 'use_crusher', False)])
        self.check_crusher.on_clicked(self.toggle_crusher)
        self._style_checkbutton(self.check_crusher, 'BitCrusher')

        # SLIDER BIT DEPTH
        ax_bits = self.control.add_axes([0.38, 0.42, 0.20, 0.03])
    
        # get initial value from effect if exists
        crusher_effect = self.effects.get('BitCrusher')
        if crusher_effect:
            initial_bits = crusher_effect.bit_depth
        else:
            initial_bits = 4

        # Limits: 1 bit (very destructive) to 16 bits (almost no effect)
        self.slider_bits = Slider(ax_bits, "Bit Depth", 1, 16,
                              valinit=initial_bits, valstep=1, valfmt='%0.0f')
        self.slider_bits.on_changed(self._on_bit_depth_changed)

        # SLIDER DOWNSAMPLE FACTOR
        ax_downsample = self.control.add_axes([0.38, 0.37, 0.20, 0.03])

        if crusher_effect:
            initial_factor = crusher_effect.downsample_factor
        else:
            initial_factor = 8

        # Limits: 1 (without reduction) to 32 (very reduced)
        self.slider_downsample = Slider(ax_downsample, "Downsample", 1, 32,
                                    valinit=initial_factor, valstep=1, valfmt='%0.0f')
        self.slider_downsample.on_changed(self._on_downsample_changed)
    
        # SLIDER MIX 
        ax_mix = self.control.add_axes([0.38, 0.32, 0.20, 0.03])
    
        if crusher_effect:
            initial_mix = crusher_effect.mix
        else:
            initial_mix = 1.0

        # Limits: 0.0 (original only) to 1.0 (crusher only)
        self.slider_mix = Slider(ax_mix, "Mix", 0.0, 1.0, 
                             valinit=initial_mix, valfmt='%0.2f')
        self.slider_mix.on_changed(self._on_crusher_mix_changed)
        
    def _on_bit_depth_changed(self, value):
        """when change the bit depth"""
        if 'BitCrusher' in self.effects:
            bits = int(value)
            self.effects['BitCrusher'].set_bit_depth(bits)
        
        
            if getattr(self, 'use_crusher', False) and self.graphs and self.guitar:
                self._refresh_current_graph()

    def _on_downsample_changed(self, value):
        """when change the downsample factor"""
        if 'BitCrusher' in self.effects:
            factor = int(value)
            self.effects['BitCrusher'].set_downsample_factor(factor)
    
        
            if getattr(self, 'use_crusher', False) and self.graphs and self.guitar:
                self._refresh_current_graph()

    def _on_crusher_mix_changed(self, value):
        """when change the mix value"""
        if 'BitCrusher' in self.effects:
            mix = float(value)
            self.effects['BitCrusher'].set_mix(mix)
        
    
            if getattr(self, 'use_crusher', False) and self.graphs and self.guitar:
                self._refresh_current_graph()
    
    def toggle_crusher(self, label):
        # synchronize state
        new_state = self.check_crusher.get_status()[0]
        self.use_bitcrusher = new_state  
    
        print(f"BitCrusher: {'ON' if self.use_bitcrusher else 'OFF'}")
        self._style_checkbutton(self.check_crusher, 'BitCrusher')

        self.control.canvas.draw_idle()
    
        if self.graphs and self.guitar:
            self._refresh_current_graph()

    def _create_distortion_panel(self):
        """Control panel for distortion parameters"""
        # Panel area
        distortion_area = self.control.add_subplot(self.gs[0, 0])
        distortion_area.set_axis_off()

        ax_title = self.control.add_axes([0.018, 0.95, 0.25, 0.04])
        ax_title.set_axis_off()
        ax_title.text(0.5, 0.5, 'DISTORTION CONTROL', 
                 ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax_oversample = self.control.add_axes([0.018, 0.65, 0.15, 0.04])
        self.check_oversample = CheckButtons(ax_oversample, ['ON - Oversampling'], 
                            [self.use_oversampling])
        self.check_oversample.on_clicked(self.toggle_oversampling)
        self._style_checkbutton(self.check_oversample, 'Oversampling')
        # Graph button
        ax_graph = self.control.add_axes([0.185, 0.90, 0.073, 0.04])  
        self.button_graph_selected = Button(ax_graph, 'Graph Effect', 
                                        color="#558cfa")
        self.button_graph_selected.on_clicked(self.show_selected_effect_graph)
    
        # toggle Distortion
        ax_distortion = self.control.add_axes([0.018, 0.90, 0.15, 0.04])
        self.check_distortion = CheckButtons(ax_distortion, ['ON - Distortion'], 
                            [self.use_distortion])
        self.check_distortion.on_clicked(self.toggle_distortion)
        self._style_checkbutton(self.check_distortion, 'Distortion')

        # Distortion SELECTOR
        ax_effect = self.control.add_axes([0.018, 0.80, 0.25, 0.1])
        self.radio_effect = RadioButtons(ax_effect, 
                    ['Hard', 'Tanh', 'Atan', 'Algebraic'])
        self.radio_effect.on_clicked(self._on_effect_changed)
    
    #  MODE SELECTOR
        ax_mode = self.control.add_axes([0.018, 0.70, 0.25, 0.1])
        self.radio_mode = RadioButtons(ax_mode,
                    ['Simétrico', 'Asim-Cut', 'Asim-Offset'])
        self.radio_mode.on_clicked(self._on_mode_changed)
    
    # DYNAMIC SLIDERS
    # umbral (always visible)
        ax_umbral = self.control.add_axes([0.05, 0.60, 0.20, 0.03])
        self.slider_umbral = Slider(ax_umbral, "Umbral", 0.01, 1.0, valinit=0.7)
        self.slider_umbral.on_changed(self._on_umbral_changed)
    
    # Variation (initially hidden)
        ax_variation = self.control.add_axes([0.05, 0.54, 0.20, 0.03])
        self.slider_variation = Slider(ax_variation, "Variation", -0.8, 0.8, valinit=0.0)
        self.slider_variation.on_changed(self._on_variation_changed)
        self.slider_variation.ax.set_visible(False)
    
    # Offset (initially hidden)
        ax_offset = self.control.add_axes([0.05, 0.54, 0.20, 0.03])
        self.slider_offset = Slider(ax_offset, "Offset", -0.8, 0.8, valinit=0.0)
        self.slider_offset.on_changed(self._on_offset_changed)
        self.slider_offset.ax.set_visible(False)
    
    # Initialize with default effect
        self._on_effect_changed('Hard')

    def toggle_distortion(self, label):
        new_state = self.check_distortion.get_status()[0]
        self.use_distortion = new_state
        # update graph if it exist
        if self.graphs and self.guitar:
            self._refresh_current_graph()
        print(f"Distortion: {'ON' if self.use_distortion else 'OFF'}")
            
        self._style_checkbutton(self.check_distortion, 'Distortion')
        self.control.canvas.draw_idle()
        
        if self.graphs and self.guitar:
            self._refresh_current_graph()
            
    def toggle_oversampling(self, label):

        new_state = self.check_oversample.get_status()[0]
        self.use_oversampling = new_state
        # update graph if it exist
        if self.graphs and self.guitar:
            self._refresh_current_graph()
        print(f"Oversampling: {'ON' if self.use_oversampling else 'OFF'}")
        
        self._style_checkbutton(self.check_oversample, 'Oversampling')
        self.control.canvas.draw_idle()
        
        if self.graphs and self.guitar:
            self._refresh_current_graph()
    
    def show_selected_effect_graph(self, event):
        """Graphing actual selected effect"""
        if not self.guitar:
            print("No guitar signal loaded.")
            return
    
        if not self.selected_clipping:
            print("No effect selected. Please select one from RadioButtons.")
            return
    
        print(f"Graphing selected effect: {self.selected_clipping}")
        self.show_current_settings_graph(event)
    
    def _on_effect_changed(self, effect_name):
        """when changes type distortion"""
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

        print(f"Distortion effect changed to: {effect_name}")

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

        print(f"Mode changed to: {mode}")

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
        """update limits of variation and offset sliders for HardClipping"""
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


    def _refresh_current_graph(self):
        # update Graphs with current configuration
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
            
        if self.use_distortion and self.selected_clipping in self.effects:
            signal = self.effects[self.selected_clipping].apply(signal)
            
        if self.use_oversampling and 'Oversampler' in self.effects:
            signal = self.effects['Oversampler'].downsample(signal)  
        
        if self.use_filter and 'Filter' in self.effects:
            signal = self.effects['Filter'].apply(signal)
            
        if self.use_delay and 'Delay' in self.effects:
            signal = self.effects['Delay'].apply(signal, self.guitar.samplerate)
        
        if self.use_reverb and 'Reverb' in self.effects:
            signal = self.effects['Reverb'].apply(signal, self.guitar.samplerate)

        if self.use_bitcrusher and 'BitCrusher' in self.effects:
            signal = self.effects['BitCrusher'].apply(signal)

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
            
    
    def show_original_signal_graph(self, event):
        self.selected_clipping = 'Original'
        
        if not self.graphs:
            self.graphs = Graphs(self.guitar, self.effects)
        
        time = time_x(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing('Original Signal', time, self.guitar.data, color='cyan')
        frequencies, magnitude = fft(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing_fft('FFT signal', frequencies, magnitude, color='red')
        F, T, S = spectrogram(self.guitar.data, self.guitar.samplerate)
        self.graphs.graphing_spectrogram('Spectrogram', T, F, S)
        self.update_gain(self.slider_gain.val)
        
    def show_bitcrusher_graph(self, event):
        self.selected_clipping = 'BitCrusher'
        self.show_current_settings_graph(event)

    def _get_effect_color(self):
        """returns color associated to the current effect"""
        colors = {
            'Hard': '#ff0000',
            'Tanh': '#ff00d0', 
            'Atan': '#51FF00',
            'Algebraic': '#00b7ff',
            'BitCrusher': '#00ffaa',
            'Original': 'cyan'
        }
        return colors.get(self.selected_clipping, '#ffffff')
    
    def _style_checkbutton(self, check, name):
        """Versión simple que solo cambia texto según estado"""
    
        # Obtener estado
        try:
            is_checked = check.get_status()[0]
        except:
            is_checked = True
    
        # Cambiar texto según estado
        if is_checked:
            new_text = f'ON - {name}'  # Con check
            text_color = '#00ff88'  # Verde
        else:
            new_text = f'OFF - {name}'  # Con cruz
            text_color = '#ff4444'  # Rojo
    
        # Actualizar texto
        for label in check.labels:
            label.set_text(new_text)
            label.set_color(text_color)
            label.set_fontsize(9)
    
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
        

_tk_root_instance = None  # global variable to hold the single Tk instance

def get_tk_root():
    """returns a single instance of Tk() for the entire application"""
    global _tk_root_instance
    if _tk_root_instance is None:
        _tk_root_instance = tk.Tk()
        _tk_root_instance.withdraw()
        # Configure to survive graph shutdowns
        _tk_root_instance.attributes('-topmost', False)
    return _tk_root_instance  
    