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
        self.iconbitmap("icon.ico")
        self.word_manager = WordManager()
        self.toaster = ToastNotifier()

        # tkinter framing
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)
        self.middle_frame = tk.Frame(self)
        self.middle_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=False)
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

         # word label and entry
        word_frame = tk.Frame(self.left_frame)
        word_frame.pack(anchor=tk.W)  # Align the frame to the left
        self.word_label = tk.Label(word_frame, text="Word:")
        self.word_label.pack(side=tk.LEFT)
        self.word_entry = tk.Entry(word_frame)
        self.word_entry.pack(side=tk.LEFT)  # Add right padding to the entry

        # definition label and entry
        definition_frame = tk.Frame(self.left_frame)
        definition_frame.pack(anchor=tk.W)  # Align the frame to the left
        self.definition_label = tk.Label(definition_frame, text="Definition:")
        self.definition_label.pack(side=tk.LEFT)
        self.definition_entry = tk.Entry(definition_frame)
        self.definition_entry.pack(side=tk.LEFT)

        # add button
        self.add_button = tk.Button(self.left_frame, text="Add Word", command=self.add_word)
        self.add_button.pack()
        
        # word listbox and label
        self.word_list_label = tk.Label(self.left_frame, text="Word List")
        self.word_list_label.pack()
        self.word_list = tk.Listbox(self.left_frame)
        self.word_list.pack(fill=tk.BOTH, expand=True)

        # timing and control buttons
        self.interval_label = tk.Label(self.middle_frame, text="Notification Interval (minutes):")
        self.interval_label.pack()
        self.interval_entry = tk.Entry(self.middle_frame)
        self.interval_entry.insert(tk.END, "1")
        self.interval_entry.pack()
        self.interval_button = tk.Button(self.middle_frame, text="Set Interval", command=self.set_interval)
        self.interval_button.pack()
        self.toggle_button = tk.Button(self.middle_frame, text="Start Notifications", command=self.toggle_notifications)
        self.toggle_button.pack()
        self.add_to_noti_button = tk.Button(self.middle_frame, text="Add to Notifications", command=self.add_to_noti_words)
        self.add_to_noti_button.pack()
        self.delete_button = tk.Button(self.middle_frame, text="Delete Word", command=self.delete_word)
        self.delete_button.pack()

        # notification words listbox and label
        self.noti_words_label = tk.Label(self.right_frame, text="Notification Words")
        self.noti_words_label.pack()
        self.noti_words_list = tk.Listbox(self.right_frame)
        self.noti_words_list.pack(fill=tk.BOTH, expand=True)

        # load words from words.json and noti_words.json
        self.load_words()
        self.load_noti_words()

        # set default notification interval
        self.interval = 5

        # system tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.hide_window)


    # save a word to the words.json file
    def add_word(self):
        # pull the word from the entry fields and add to word_manager
        word = self.word_entry.get()
        definition = self.definition_entry.get()
        self.word_manager.add_word(word, definition)

        # clear the fields
        self.word_entry.delete(0, tk.END)
        self.definition_entry.delete(0, tk.END)
        self.load_words()

    # load all the words into gui word_list
    def load_words(self):
        self.word_list.delete(0, tk.END)
        words = self.word_manager.get_words()
        for word, definition in words.items():
            self.word_list.insert(tk.END, f"{word}: {definition}")

    # load all the words from noti_words.json
    def load_noti_words(self):
        self.noti_words_list.delete(0, tk.END)
        for word in self.word_manager.noti_words:
            self.noti_words_list.insert(tk.END, word)

    # function for thread to call to display a toast every interval
    # loops through all notification words (currently not random)
    def display_notifications(self):
        while not self.notification_thread_stop_event.is_set():
            if self.word_manager.noti_words:
                noti_words = self.word_manager.get_noti_words()
                for word, definition in noti_words.items():
                    if self.notification_thread_stop_event.is_set():
                        break
                    self.toaster.show_toast(word, definition, icon_path="icon.ico", duration=3)
                    time.sleep(self.interval)
            else:
                time.sleep(self.interval)

    # function to toggle the notification thread on or off (restarts)
    def toggle_notifications(self):
        if not hasattr(self, 'notification_thread') or not self.notification_thread.is_alive():
            self.notification_thread_stop_event = threading.Event()
            self.notification_thread = threading.Thread(target=self.display_notifications, daemon=True)
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
            self.word_manager.add_to_noti_words(word, word[definition])
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

    # function to set the interval of notifcations
    def set_interval(self):
        try:
            interval_minutes = int(self.interval_entry.get())
            self.interval = interval_minutes * 60  # convert minutes to seconds
        except ValueError:
            pass

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
