import tkinter as tk
from word_manager import WordManager
from win10toast import ToastNotifier
import threading
import time
import sys
import pystray
from pystray import Icon as icon, MenuItem as item
from PIL import Image


class platinum(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("platinum")
        self.geometry("800x600")

        self.word_manager = WordManager()
        self.toaster = ToastNotifier()

        self.word_entry = tk.Entry(self)
        self.word_entry.pack()

        self.add_button = tk.Button(self, text="Add Word", command=self.add_word)
        self.add_button.pack()

        self.word_list = tk.Listbox(self)
        self.word_list.pack()

        self.load_words()

        # set up notification thread
        self.notification_thread_stop_event = threading.Event()
        self.notification_thread = threading.Thread(target=self.display_notifications, args=(5,), daemon=True)
        self.notification_thread.start()

        # toggle
        self.toggle_button = tk.Button(self, text="Toggle Notifications", command=self.toggle_notifications)
        self.toggle_button.pack()

        # run in background whenever program is closed
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def add_word(self):
        word = self.word_entry.get()
        self.word_manager.add_word(word)
        self.word_entry.delete(0, tk.END)
        self.load_words()

    def load_words(self):
        self.word_list.delete(0, tk.END)
        words = self.word_manager.get_words()
        for word in words:
            self.word_list.insert(tk.END, word)

    def display_notifications(self, interval):
        words = self.word_manager.get_words()
        index = 0

        while not self.notification_thread_stop_event.is_set():
            if not self.notification_thread_stop_event.is_set():
                if words:
                    word = words[index]
                    self.toaster.show_toast("platinum", word, icon_path="icon.ico", duration=1)
                    index = (index + 1) % len(words)
                    time.sleep(interval)
                else:
                    time.sleep(1)
            else:
                time.sleep(1)

    def toggle_notifications(self):
        if self.notification_thread_stop_event.is_set():
            self.notification_thread_stop_event.clear()
            self.toggle_button.config(text="Pause Notifications")
        else:
            self.notification_thread_stop_event.set()
            self.toggle_button.config(text="Resume Notifications")
            self.notification_thread.start()

    def quit(self):
        self.stop_notification_thread()
        self.destroy()
        sys.exit()

    def stop_notification_thread(self):
        if self.notification_thread.is_alive():
            self.notification_thread_stop_event.set()
            self.notification_thread.join()

    def hide_window(self):
        self.withdraw()
        image = Image.open("icon.ico")
        menu = (item('Quit', self.quit), item('Show', self.show_window))
        icon = pystray.Icon("name", image, "platinum", menu)
        icon.run_detached()

    def show_window(self):
        self.deiconify()
