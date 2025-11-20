import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from core.adb_manager import ADBManager
from core.ocr_manager import OCRManager
from core.bot_engine import DamaiBot

class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Damai Ticket Bot (Android/ADB)")
        self.root.geometry("600x400")

        # Initialize Core Components
        self.adb = ADBManager()
        self.ocr = OCRManager()
        self.bot = DamaiBot(self.adb, self.ocr)
        self.bot.set_logger(self.log_message)

        self._create_widgets()

    def _create_widgets(self):
        # Control Frame
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill=tk.X)

        self.btn_start = tk.Button(control_frame, text="Start Bot", bg="green", fg="white", command=self.start_bot)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(control_frame, text="Stop Bot", bg="red", fg="white", command=self.stop_bot, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.btn_check = tk.Button(control_frame, text="Check Device", command=self.check_device)
        self.btn_check.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.lbl_status = tk.Label(self.root, text="Status: Idle", fg="blue")
        self.lbl_status.pack()

        # Log Area
        self.log_area = scrolledtext.ScrolledText(self.root, state='disabled', height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log_message(self, msg):
        """Thread-safe logging to GUI"""
        def _log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_area.see(tk.END)
            self.log_area.config(state='disabled')

        self.root.after(0, _log)

    def check_device(self):
        devices = self.adb.get_connected_devices()
        if devices:
            self.log_message(f"Connected devices: {devices}")
            self.lbl_status.config(text=f"Connected: {devices[0]}")
        else:
            self.log_message("No devices found. Please connect phone and enable USB debugging.")
            self.lbl_status.config(text="Status: No Device")

    def start_bot(self):
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.lbl_status.config(text="Status: Running")
        self.bot.start()

    def stop_bot(self):
        self.bot.stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.lbl_status.config(text="Status: Stopped")

def main():
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
