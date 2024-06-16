import tkinter as tk
from word_manager import WordManager, Vocab, Group
from win10toast import ToastNotifier
import threading
import time
import sys
import pystray
from pystray import Icon as icon, MenuItem as item
from PIL import Image
from tkinter import filedialog, messagebox

# Sean Beaulieu

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

        # group label and entry
        group_frame = tk.Frame(self.left_frame)
        group_frame.pack(anchor=tk.W)
        self.group_label = tk.Label(group_frame, text="Group:")
        self.group_label.pack(side=tk.LEFT)
        self.group_entry = tk.Entry(group_frame)
        self.group_entry.pack(side=tk.LEFT)

        # word label and entry
        word_frame = tk.Frame(self.left_frame)
        word_frame.pack(anchor=tk.W)
        self.word_label = tk.Label(word_frame, text="Word:")
        self.word_label.pack(side=tk.LEFT)
        self.word_entry = tk.Entry(word_frame)
        self.word_entry.pack(side=tk.LEFT)

        # definition label and entry
        definition_frame = tk.Frame(self.left_frame)
        definition_frame.pack(anchor=tk.W)
        self.definition_label = tk.Label(definition_frame, text="Definition:")
        self.definition_label.pack(side=tk.LEFT)
        self.definition_entry = tk.Entry(definition_frame)
        self.definition_entry.pack(side=tk.LEFT)

        # add group and word buttons
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack()
        self.add_group_button = tk.Button(button_frame, text="Add Group", command=self.add_group)
        self.add_group_button.pack(side=tk.LEFT)
        self.add_word_button = tk.Button(button_frame, text="Add Word", command=self.add_word)
        self.add_word_button.pack(side=tk.LEFT)
        self.import_button = tk.Button(button_frame, text="Import CSV", command=self.import_csv)
        self.import_button.pack(side=tk.LEFT)
        

        # group listbox and label
        self.group_list_label = tk.Label(self.left_frame, text="Groups")
        self.group_list_label.pack()
        self.group_list = tk.Listbox(self.left_frame)
        self.group_list.pack(fill=tk.BOTH, expand=True)
        self.group_list.bind("<<ListboxSelect>>", self.select_group)

        # word listbox and label
        self.word_list_label = tk.Label(self.right_frame, text="Words")
        self.word_list_label.pack()
        self.word_list = tk.Listbox(self.right_frame)
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
        self.delete_group_button = tk.Button(self.middle_frame, text="Delete Group", command=self.delete_group)
        self.delete_group_button.pack()
        self.delete_word_button = tk.Button(self.middle_frame, text="Delete Word", command=self.delete_word)
        self.delete_word_button.pack()

        # toggle word and group active buttons
        self.toggle_group_button = tk.Button(self.middle_frame, text="Toggle Group Active", command=self.toggle_group_active)
        self.toggle_group_button.pack()
        self.toggle_word_button = tk.Button(self.middle_frame, text="Toggle Word Active", command=self.toggle_word_active)
        self.toggle_word_button.pack()

        # load groups and words
        self.load_groups()

        # set default notification interval
        self.interval = 5

        # system tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    def add_group(self):
        group_name = self.group_entry.get()
        self.word_manager.add_group(group_name)
        self.group_entry.delete(0, tk.END)
        self.load_groups()

    def add_word(self):
        group_name = self.group_entry.get()
        word = self.word_entry.get()
        definition = self.definition_entry.get()
        self.word_manager.add_vocab(group_name, word, definition)
        self.word_entry.delete(0, tk.END)
        self.definition_entry.delete(0, tk.END)
        self.load_words()

    # import csv
    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            group_name = self.group_entry.get()
            if not group_name:
                messagebox.showerror("Error", "Please enter a group name.")
                return
            if not any(group.name == group_name for group in self.word_manager.get_groups()):
                self.word_manager.add_group(group_name)
            self.word_manager.import_vocab_from_csv(group_name, file_path)
            self.load_groups()
            self.group_entry.delete(0, tk.END)
            self.group_entry.insert(tk.END, group_name)
            self.load_words()

    def load_groups(self):
        self.group_list.delete(0, tk.END)
        groups = self.word_manager.get_groups()
        for group in groups:
            if group.active:
                self.group_list.insert(tk.END, group.name)
            else:
                self.group_list.insert(tk.END, group.name)
                self.group_list.itemconfig(tk.END, fg="gray")

    def load_words(self):
        self.word_list.delete(0, tk.END)
        group_name = self.group_entry.get()
        vocab_list = self.word_manager.get_vocab_list(group_name)
        for vocab in vocab_list:
            if vocab.active:
                self.word_list.insert(tk.END, f"{vocab.word}: {vocab.definition}")
            else:
                self.word_list.insert(tk.END, f"{vocab.word}: {vocab.definition}")
                self.word_list.itemconfig(tk.END, fg="gray")

    def select_group(self, event):
        selected_group = self.group_list.get(self.group_list.curselection())
        self.group_entry.delete(0, tk.END)
        self.group_entry.insert(tk.END, selected_group)
        self.load_words()

    # notifications
    def display_notifications(self):
        while not self.notification_thread_stop_event.is_set():
            groups = self.word_manager.get_groups()
            for group in groups:
                if group.active:
                    vocab_list = group.vocab_list
                    for vocab in vocab_list:
                        if vocab.active:
                            if self.notification_thread_stop_event.is_set():
                                break
                            self.toaster.show_toast(vocab.word, vocab.definition, icon_path="icon.ico", duration=3)
                            time.sleep(self.interval)
            time.sleep(self.interval)

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

    # group and word 'active' setters
    def toggle_group_active(self):
        selected_group = self.group_list.get(self.group_list.curselection())
        group = next((group for group in self.word_manager.get_groups() if group.name == selected_group), None)
        if group:
            self.word_manager.set_group_active(selected_group, not group.active)
            self.load_groups()

    def toggle_word_active(self):
        group_name = self.group_entry.get()
        selected_word = self.word_list.get(self.word_list.curselection())
        word = selected_word.split(":")[0].strip()
        vocab = next((vocab for vocab in self.word_manager.get_vocab_list(group_name) if vocab.word == word), None)
        if vocab:
            self.word_manager.set_vocab_active(group_name, word, not vocab.active)
            self.load_words()

    def delete_group(self):
        selected_group = self.group_list.get(self.group_list.curselection())
        self.word_manager.delete_group(selected_group)
        self.load_groups()
        self.word_list.delete(0, tk.END)

    # grabs the word by getting string before ':'
    def delete_word(self):
        group_name = self.group_entry.get()
        selected_word = self.word_list.get(self.word_list.curselection())
        word = selected_word.split(":")[0].strip()
        self.word_manager.delete_vocab(group_name, word)
        self.load_words()

    def set_interval(self):
        try:
            interval_minutes = int(self.interval_entry.get())
            self.interval = interval_minutes * 60  # convert minutes to seconds
        except ValueError:
            pass

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

    def stop_notification_thread(self):
        if hasattr(self, 'notification_thread') and self.notification_thread.is_alive():
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
