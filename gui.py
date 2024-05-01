import tkinter as tk
from word_manager import WordManager
from win10toast import ToastNotifier
import threading
import time
import sys
import pystray
from pystray import Icon as icon, MenuItem as item
from PIL import Image

class Platinum(tk.Tk):
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
        self.noti_words_list = tk.Listbox(self)
        self.noti_words_list.pack()
        self.load_words()
        self.load_noti_words()

        # Set up notification thread
        self.notification_thread_stop_event = threading.Event()
        self.notification_thread = threading.Thread(target=self.display_notifications, args=(5,), daemon=True)
        self.notification_thread.start()

        # Toggle notification button
        self.toggle_button = tk.Button(self, text="Pause Notifications", command=self.toggle_notifications)
        self.toggle_button.pack()

        # Add/Delete buttons
        self.add_to_noti_button = tk.Button(self, text="Add to Notifications", command=self.add_to_noti_words)
        self.add_to_noti_button.pack()
        self.delete_button = tk.Button(self, text="Delete Word", command=self.delete_word)
        self.delete_button.pack()

        # System tray
        self.tray_icon = None
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

    def load_noti_words(self):
        self.noti_words_list.delete(0, tk.END)
        for word in self.word_manager.noti_words:
            self.noti_words_list.insert(tk.END, word)

    def display_notifications(self, interval):
        while not self.notification_thread_stop_event.is_set():
            if self.word_manager.noti_words:
                word = self.word_manager.noti_words[0]
                self.toaster.show_toast("platinum", word, icon_path="icon.ico", duration=1)
                self.word_manager.noti_words.pop(0)
                self.load_noti_words()
            time.sleep(interval)

    def toggle_notifications(self):
        if self.notification_thread_stop_event.is_set():
            self.notification_thread_stop_event.clear()
            self.toggle_button.config(text="Pause Notifications")
        else:
            self.notification_thread_stop_event.set()
            self.toggle_button.config(text="Resume Notifications")

    def add_to_noti_words(self):
        selected = self.word_list.curselection()
        if selected:
            word = self.word_list.get(selected)
            self.word_manager.add_to_noti_words(word)
            self.load_noti_words()

    def delete_word(self):
        selected = self.word_list.curselection()
        if selected:
            word = self.word_list.get(selected)
            self.word_manager.delete_word(word)
            self.load_words()
        selected = self.noti_words_list.curselection()
        if selected:
            word = self.noti_words_list.get(selected)
            self.word_manager.delete_word(word)
            self.load_noti_words()

    def quit(self):
        self.stop_notification_thread()
        if self.tray_icon:
            self.tray_icon.stop()
        try:
            self.destroy()
            sys.exit()
        except SystemExit:
            pass

    def stop_notification_thread(self):
        if self.notification_thread.is_alive():
            self.notification_thread_stop_event.set()
            self.notification_thread.join()

    def hide_window(self):
        self.iconify()
        image = Image.open("icon.ico")
        menu = (item('Quit', self.quit), item('Show', self.show_window))
        self.tray_icon = pystray.Icon("platinum", image, "platinum", menu)
        self.tray_icon.run_detached()

    def show_window(self):
        self.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
