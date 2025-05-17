import tkinter as tk
from tkinter import ttk
import pyperclip
from googletrans import Translator, LANGUAGES
import threading
import time
from gtts import gTTS
from playsound import playsound
import os


class FloatingTranslator:
    def __init__(self):
        self.dest_language = 'en'
        self.translator = Translator()
        self.last_text = ""
        self.running = True

        # Initialize window
        self.root = tk.Tk()
        self.root.title("Translator Widget")
        self.root.geometry("350x200+1000+100")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)

        # DARK MODE Colors
        bg_color = "#1e1e1e"
        fg_color = "#f1f1f1"
        entry_bg = "#2d2d2d"

        self.root.configure(bg=bg_color)

        # Dropdown for language selection
        self.lang_var = tk.StringVar(value='en')
        self.dropdown = ttk.Combobox(self.root, textvariable=self.lang_var, state='readonly')
        self.dropdown['values'] = sorted([f"{code} - {name.title()}" for code, name in LANGUAGES.items()])
        self.dropdown.bind("<<ComboboxSelected>>", self.change_language)
        self.dropdown.place(x=10, y=10, width=330)

        # Label for translation
        self.text_label = tk.Label(
            self.root,
            text="Waiting for text...",
            wraplength=320,
            justify="left",
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 10)
        )
        self.text_label.place(x=10, y=50)

        # Add drag support
        self.offset_x = 0
        self.offset_y = 0
        self.text_label.bind("<Button-1>", self.click_window)
        self.text_label.bind("<B1-Motion>", self.drag_window)
        self.dropdown.bind("<Button-1>", self.click_window)
        self.dropdown.bind("<B1-Motion>", self.drag_window)

        # Close button
        self.close_btn = tk.Button(
            self.root,
            text="✕",
            command=self.close,
            bg=bg_color,
            fg=fg_color,
            border=0,
            font=("Segoe UI", 10)
        )
        self.close_btn.place(x=320, y=5, width=20, height=20)

        # Speak button
        self.speak_btn = tk.Button(
            self.root,
            text="🔊",
            command=self.speak_translation,
            bg=bg_color,
            fg=fg_color,
            border=0,
            font=("Segoe UI", 12)
        )
        self.speak_btn.place(x=290, y=5, width=30, height=30)

        # Start clipboard monitor
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitor_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()

    def change_language(self, event):
        selected = self.lang_var.get()
        self.dest_language = selected.split(" - ")[0]

    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def monitor_clipboard(self):
        while self.running:
            try:
                text = pyperclip.paste()
                if text != self.last_text and isinstance(text, str) and len(text.strip()) > 0:
                    self.last_text = text
                    translation = self.translator.translate(text, dest=self.dest_language)
                    self.update_text(translation.text)
            except Exception as e:
                self.update_text(f"Error: {str(e)}")
            time.sleep(1)

    def update_text(self, new_text):
        self.text_label.config(text=new_text)

    def speak_translation(self):
        text = self.text_label.cget("text")
        if not text or "Error" in text or text == "Waiting for text...":
            return
        try:
            tts = gTTS(text=text, lang=self.dest_language)
            filename = "temp_audio.mp3"
            tts.save(filename)
            playsound(filename)
            os.remove(filename)
        except Exception as e:
            self.update_text(f"TTS Error: {str(e)}")

    def close(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    FloatingTranslator()
