import tkinter as tk
import numpy as np
import sounddevice as sd

# Generate all 88 piano notes, frequencies, and types programmatically
NOTE_NAMES = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
PIANO_KEYS = []

for n in range(1, 89):
    name_idx = (n - 1) % 12
    note_name = NOTE_NAMES[name_idx]
    
    if n <= 3:
        octave = 0
    else:
        octave = (n - 4) // 12 + 1
        
    full_name = f"{note_name}{octave}"
    # Standard formula mapped relative to A4 (440Hz)
    freq = 440.0 * (2.0 ** ((n - 49) / 12.0))
    is_black = '#' in note_name
    
    PIANO_KEYS.append({
        'name': full_name,
        'freq': freq,
        'type': 'black' if is_black else 'white',
        'index': n
    })

def play_piano_sound(frequency, duration=2.0, sample_rate=44100):
    """Synthesizes a full, massive acoustic piano sound with 8 harmonic layers."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 8-Overtone rich harmonic layer mix for a deep, massive concert grand piano profile
    wave = (1.20 * np.sin(2 * np.pi * frequency * t) +
            0.75 * np.sin(2 * np.pi * 2 * frequency * t) +
            0.45 * np.sin(2 * np.pi * 3 * frequency * t) +
            0.30 * np.sin(2 * np.pi * 4 * frequency * t) +
            0.15 * np.sin(2 * np.pi * 5 * frequency * t) +
            0.08 * np.sin(2 * np.pi * 6 * frequency * t) +
            0.04 * np.sin(2 * np.pi * 7 * frequency * t) +
            0.02 * np.sin(2 * np.pi * 8 * frequency * t))
    
    # Natural exponential string-damping envelope curve
    envelope = np.exp(-1.8 * t)
    piano_sound = wave * envelope
    
    # Soft limiter to normalize the multi-harmonic stacking without digital clipping distortion
    piano_sound = piano_sound / np.max(np.abs(piano_sound)) * 0.50
    sd.play(piano_sound, sample_rate)

class MassivePianoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Concert Grand Piano - Massive Sound (1000 Hz Master Mode)")
        self.root.geometry("1460x380")
        self.root.configure(bg="#11161b")
        
        self.keyboard_map = {
            'a': 0, 'w': 1, 's': 2, 'e': 3, 'd': 4, 'f': 5, 't': 6, 'g': 7, 'y': 8, 'h': 9, 'u': 10, 'j': 11,
            'k': 12, 'o': 13, 'l': 14, 'p': 15, 'semicolon': 16
        }
        
        self.current_octave_offset = 27 
        self.white_buttons = {}
        self.black_buttons = {}
        
        self.create_status_bar()
        self.create_piano_keyboard()
        self.bind_controls()

    def create_status_bar(self):
        # Header display with high-contrast text layout
        self.status_label = tk.Label(
            self.root, 
            text="Use LEFT / RIGHT ARROW keys to shift your active computer keyboard block!",
            bg="#11161b", fg="#00ffcc", font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=10)
        
        # Secondary indicator for the 1000Hz master test tone option
        test_btn = tk.Button(
            self.root, text="🔊 Play 1000Hz Reference Tone", font=("Arial", 10, "bold"),
            bg="#00ffcc", fg="#11161b", activebackground="#00cc99",
            command=lambda: play_piano_sound(1000.0)
        )
        test_btn.pack(pady=5)

    def create_piano_keyboard(self):
        container = tk.Frame(self.root, bg="#11161b")
        container.pack(fill="both", expand=True, padx=15, pady=5)

        white_w = 26  
        white_h = 220 
        w_count = 0
        
        for key in PIANO_KEYS:
            if key['type'] == 'white':
                x_pos = w_count * (white_w + 1)
                btn = tk.Button(
                    container, bg="#ffffff", fg="#11161b", text=key['name'],
                    font=("Arial", 11, "bold"), anchor="s", bd=2, relief="raised",
                    command=lambda f=key['freq']: play_piano_sound(f)
                )
                btn.place(x=x_pos, y=0, width=white_w, height=white_h)
                self.white_buttons[key['index']] = btn
                w_count += 1

        w_count = 0
        for key in PIANO_KEYS:
            if key['type'] == 'white':
                w_count += 1
            else:
                black_w = 18   
                black_h = 135  
                x_pos = (w_count * 27) - (black_w // 2) - 1
                
                btn = tk.Button(
                    container, bg="#2c3e50", fg="#ffffff", activebackground="#34495e",
                    text=key['name'], font=("Arial", 8, "bold"), anchor="s",
                    bd=1, relief="raised", command=lambda f=key['freq']: play_piano_sound(f)
                )
                btn.place(x=x_pos, y=0, width=black_w, height=black_h)
                self.black_buttons[key['index']] = btn

    def bind_controls(self):
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<Left>", lambda e: self.shift_octave(-12))
        self.root.bind("<Right>", lambda e: self.shift_octave(12))

    def shift_octave(self, amount):
        new_offset = self.current_octave_offset + amount
        if 1 <= new_offset <= 72:
            self.current_octave_offset = new_offset
            start_note = PIANO_KEYS[self.current_octave_offset]['name']
            self.status_label.config(text=f"Focus shifted! Typing key 'A' is bound to: {start_note}")

    def on_key_press(self, event):
        key_char = event.keysym.lower()
        if key_char in self.keyboard_map:
            target_idx = self.current_octave_offset + self.keyboard_map[key_char]
            if target_idx < len(PIANO_KEYS):
                key_data = PIANO_KEYS[target_idx]
                
                if key_data['type'] == 'white' and target_idx in self.white_buttons:
                    self.white_buttons[target_idx].config(bg="#00ffcc")
                elif key_data['type'] == 'black' and target_idx in self.black_buttons:
                    self.black_buttons[target_idx].config(bg="#e74c3c")
                    
                play_piano_sound(key_data['freq'])

    def on_key_release(self, event):
        key_char = event.keysym.lower()
        if key_char in self.keyboard_map:
            target_idx = self.current_octave_offset + self.keyboard_map[key_char]
            if target_idx < len(PIANO_KEYS):
                key_data = PIANO_KEYS[target_idx]
                if key_data['type'] == 'white' and target_idx in self.white_buttons:
                    self.white_buttons[target_idx].config(bg="#ffffff")
                elif key_data['type'] == 'black' and target_idx in self.black_buttons:
                    self.black_buttons[target_idx].config(bg="#2c3e50")

if __name__ == "__main__":
    root = tk.Tk()
    app = MassivePianoApp(root)
    root.mainloop()

