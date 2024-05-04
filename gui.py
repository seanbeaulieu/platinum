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

        # toggle notification button
        self.toggle_button = tk.Button(self, text="Start Notifications", command=self.toggle_notifications)
        self.toggle_button.pack()

        # add/delete buttons
        self.add_to_noti_button = tk.Button(self, text="Add to Notifications", command=self.add_to_noti_words)
        self.add_to_noti_button.pack()
        self.delete_button = tk.Button(self, text="Delete Word", command=self.delete_word)
        self.delete_button.pack()

        # system tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    # save a word to the words.json file
    def add_word(self):
        word = self.word_entry.get()
        self.word_manager.add_word(word)
        self.word_entry.delete(0, tk.END)
        self.load_words()

    # load all the words into gui word_list
    def load_words(self):
        self.word_list.delete(0, tk.END)
        words = self.word_manager.get_words()
        for word in words:
            self.word_list.insert(tk.END, word)

    # load all the words from noti_words.json
    def load_noti_words(self):
        self.noti_words_list.delete(0, tk.END)
        for word in self.word_manager.noti_words:
            self.noti_words_list.insert(tk.END, word)

    # function for thread to call to display a toast every interval
    # loops through all notification words (currently not random)
    def display_notifications(self, interval):
        while not self.notification_thread_stop_event.is_set():
            if self.word_manager.noti_words:
                for word in self.word_manager.noti_words:
                    if self.notification_thread_stop_event.is_set():
                        break
                    self.toaster.show_toast("platinum", word, icon_path="icon.ico", duration=1)
                    time.sleep(interval)
            else:
                time.sleep(interval)

    # function to toggle the notification thread on or off (restarts)
    def toggle_notifications(self):
        if not hasattr(self, 'notification_thread') or not self.notification_thread.is_alive():
            self.notification_thread_stop_event = threading.Event()
            self.notification_thread = threading.Thread(target=self.display_notifications, args=(5,), daemon=True)
            self.notification_thread.start()
            self.toggle_button.config(text="Pause Notifications")
        else:
            self.notification_thread_stop_event.set()
            self.notification_thread.join()
            self.toggle_button.config(text="Resume Notifications")

    # add a word from word_list to noti_words_list
    def add_to_noti_words(self):
        selected = self.word_list.curselection()
        if selected:
            word = self.word_list.get(selected)
            self.word_manager.add_to_noti_words(word)
            self.load_noti_words()

    # remove a word from either list
    def delete_word(self):
        selected = self.word_list.curselection()
        if selected:
            word = self.word_list.get(selected)
            self.word_manager.delete_word(word)
            self.load_words()
        selected = self.noti_words_list.curselection()
        if selected:
            word = self.noti_words_list.get(selected)
            self.word_manager.remove_from_noti_words(word)
            self.load_noti_words()

    # system tray icon to exit the app
    def quit(self):
        if hasattr(self, 'notification_thread'):
            self.stop_notification_thread()
        if self.tray_icon:
            self.tray_icon.stop()
        try:
            self.destroy()
            sys.exit()
        except SystemExit:
            pass

    # stop notifications function
    def stop_notification_thread(self):
        if hasattr(self, 'notification_thread') and self.notification_thread.is_alive():
            self.notification_thread_stop_event.set()
            self.notification_thread.join()

    # on closing the app, minimizes it to system tray instead
    def hide_window(self):
        self.iconify()
        image = Image.open("icon.ico")
        menu = (item('Quit', self.quit), item('Show', self.show_window))
        self.tray_icon = pystray.Icon("platinum", image, "platinum", menu)
        self.tray_icon.run_detached()

    # system tray icon function to reopen window
    def show_window(self):
        self.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
