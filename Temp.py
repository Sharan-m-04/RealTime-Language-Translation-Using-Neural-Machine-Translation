import os
import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread, Lock
from typing import Dict
import time
import logging
from PIL import Image
import easyocr
from deep_translator import GoogleTranslator

#Main Function to Translate the languages
class LanguageTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translator")

        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.languages: Dict[str, str] = {
            'English': 'en',
            'Tamil': 'ta',
            'Hindi': 'hi',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Chinese (Simplified)': 'zh-cn',
            'Japanese': 'ja',
            'Korean': 'ko'
        }
        self.translation_lock = Lock()
        self.translation_thread = None
        self.debounce_delay = 0.2
        self.last_keypress_time = time.time()

        self.setup_logging()
        self.create_widgets()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.text_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.text_tab, text='Text Translation')
        self.create_text_tab_widgets()

        self.image_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.image_tab, text='Image Translation')
        self.create_image_tab_widgets()

        self.tab_control.pack(expand=1, fill='both')

    def create_text_tab_widgets(self):
        src_lang_label = tk.Label(self.text_tab, text="Source Language:")
        src_lang_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_lang_combo = ttk.Combobox(self.text_tab, values=list(self.languages.keys()))
        self.src_lang_combo.grid(row=0, column=1, padx=10, pady=10)
        self.src_lang_combo.current(0)

        tgt_lang_label = tk.Label(self.text_tab, text="Target Language:")
        tgt_lang_label.grid(row=1, column=0, padx=10, pady=10)

        self.tgt_lang_combo = ttk.Combobox(self.text_tab, values=list(self.languages.keys()))
        self.tgt_lang_combo.grid(row=1, column=1, padx=10, pady=10)
        self.tgt_lang_combo.current(1)

        input_text_label = tk.Label(self.text_tab, text="Input Text:")
        input_text_label.grid(row=2, column=0, padx=10, pady=10)

        self.input_text = tk.Text(self.text_tab, height=10, width=50)
        self.input_text.grid(row=2, column=1, padx=10, pady=10)
        self.input_text.bind("<KeyRelease>", self.on_text_change)

        output_text_label = tk.Label(self.text_tab, text="Translated Text:")
        output_text_label.grid(row=3, column=0, padx=10, pady=10)

        self.output_text = tk.Text(self.text_tab, height=10, width=50)
        self.output_text.grid(row=3, column=1, padx=10, pady=10)

        translate_button = ttk.Button(self.text_tab, text="Translate", command=self.translate_text)
        translate_button.place(x=540, y=280)

        clear_button = ttk.Button(self.text_tab, text="Clear", command=self.clear_text)
        clear_button.place(x=540, y=90)

    def create_image_tab_widgets(self):
        src_lang_label = tk.Label(self.image_tab, text="Source Language:")
        src_lang_label.place(x=10, y=10)

        self.src_lang_combo_img = ttk.Combobox(self.image_tab, values=list(self.languages.keys()))
        self.src_lang_combo_img.place(x=150, y=10)
        self.src_lang_combo_img.current(0)

        tgt_lang_label = tk.Label(self.image_tab, text="Target Language:")
        tgt_lang_label.place(x=10, y=40)

        self.tgt_lang_combo_img = ttk.Combobox(self.image_tab, values=list(self.languages.keys()))
        self.tgt_lang_combo_img.place(x=150, y=40)
        self.tgt_lang_combo_img.current(1)

        upload_button = ttk.Button(self.image_tab, text="Upload Image", command=self.upload_image)
        upload_button.place(x=10, y=70)

        self.image_label = tk.Label(self.image_tab, text="Uploaded Image: None")
        self.image_label.place(x=10, y=100)

        self.image_text = tk.Text(self.image_tab)
        self.image_text.place(x=10, y=310, width=680, height=210)

        translate_button = ttk.Button(self.image_tab, text="Translate", command=self.translate_image_text)
        translate_button.place(x=610, y=530)

        clear_button_img = ttk.Button(self.image_tab, text="Clear", command=self.clear_image_text)
        clear_button_img.place(x=540, y=90)

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            self.image_label.config(text=f"Uploaded Image: {file_name}")
            self.image_text.delete("1.0", tk.END)

            image = Image.open(file_path)

            reader = easyocr.Reader(['en'])

            try:
                result = reader.readtext(image, detail=0)
                extracted_text = "\n".join(result)
                self.image_text.insert(tk.END, extracted_text)
            except Exception as e:
                self.logger.error(f"OCR Error: {e}")
                self.image_text.insert(tk.END, f"OCR Error: {e}")

    def translate_image_text(self):
        src_lang = self.languages[self.src_lang_combo_img.get()]
        tgt_lang = self.languages[self.tgt_lang_combo_img.get()]

        text = self.image_text.get("1.0", tk.END).strip()

        if text:
            try:
                translation = GoogleTranslator(source=src_lang, target=tgt_lang).translate(text)
                with self.translation_lock:
                    self.image_text.delete("1.0", tk.END)
                    self.image_text.insert(tk.END, translation)
            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                with self.translation_lock:
                    self.image_text.delete("1.0", tk.END)
                    self.image_text.insert(tk.END, f"Translation error: {e}")

    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)

    def clear_image_text(self):
        self.image_text.delete("1.0", tk.END)

    def translate_text(self):
        src_lang = self.languages[self.src_lang_combo.get()]
        tgt_lang = self.languages[self.tgt_lang_combo.get()]
        text = self.input_text.get("1.0", tk.END).strip()

        if text:
            try:
                translation = GoogleTranslator(source=src_lang, target=tgt_lang).translate(text)
                with self.translation_lock:
                    self.output_text.delete("1.0", tk.END)
                    self.output_text.insert(tk.END, translation)
            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                with self.translation_lock:
                    self.output_text.delete("1.0", tk.END)
                    self.output_text.insert(tk.END, f"Translation error: {e}")

    def on_text_change(self, event=None):
        self.last_keypress_time = time.time()
        if not self.translation_thread or not self.translation_thread.is_alive():
            self.translation_thread = Thread(target=self.debounce_translation)
            self.translation_thread.start()

    def debounce_translation(self):
        while time.time() - self.last_keypress_time < self.debounce_delay:
            time.sleep(0.05)
        if time.time() - self.last_keypress_time >= self.debounce_delay:
            self.translate_text()

#main function
if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslatorApp(root)
    root.mainloop()
