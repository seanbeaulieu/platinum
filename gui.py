import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from word_manager import WordManager, Vocab, Group
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
        self.title("Platinum")
        self.geometry("1000x600")
        self.iconbitmap("icon.ico")
        self.configure(bg="#2C2F33")
        self.word_manager = WordManager()
        self.toaster = ToastNotifier()

        # Initital thread doesn't exist 
        self.notification_thread = None
        self.notification_stop_event = threading.Event()
        self.interval = 60  # Default is 1 minute

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()

        # Set up tkinter widgets on start 
        self.create_widgets()
        
        # Load groups on startup
        self.load_groups()

        # System tray
        self.tray_icon = None
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

    # Dark mode style for widgets
    def configure_styles(self):
        self.style.configure('TFrame', background="#2C2F33")
        self.style.configure('TLabel', background="#2C2F33", foreground="#FFFFFF")
        self.style.configure('TEntry', fieldbackground="#23272A", foreground="#FFFFFF")
        self.style.map('TEntry', fieldbackground=[('readonly', '#23272A')])
        self.style.configure('TButton', background="#7289DA", foreground="#FFFFFF")
        self.style.map('TButton', background=[('active', '#677BC4')])
        self.style.configure('TListbox', background="#23272A", foreground="#FFFFFF")

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # Group Management
        group_frame = ttk.Frame(left_frame)
        group_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(group_frame, text="Group:").pack(side=tk.LEFT)
        self.group_entry = ttk.Entry(group_frame)
        self.group_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        group_buttons_frame = ttk.Frame(left_frame)
        group_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(group_buttons_frame, text="Add Group", command=self.add_group).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(group_buttons_frame, text="Delete Group", command=self.delete_group).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(group_buttons_frame, text="Toggle Group Active", command=self.toggle_group_active).pack(side=tk.LEFT)

        # Group List
        self.group_list = tk.Listbox(left_frame, bg="#23272A", fg="#FFFFFF", selectbackground="#7289DA")
        self.group_list.pack(fill=tk.BOTH, expand=True)
        self.group_list.bind("<<ListboxSelect>>", self.select_group)

        # Word Management
        word_frame = ttk.Frame(right_frame)
        word_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(word_frame, text="Word:").pack(side=tk.LEFT)
        self.word_entry = ttk.Entry(word_frame)
        self.word_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        ttk.Label(word_frame, text="Definition:").pack(side=tk.LEFT, padx=(10, 0))
        self.definition_entry = ttk.Entry(word_frame)
        self.definition_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        word_buttons_frame = ttk.Frame(right_frame)
        word_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(word_buttons_frame, text="Add Word", command=self.add_word).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(word_buttons_frame, text="Delete Word", command=self.delete_word).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(word_buttons_frame, text="Toggle Word Active", command=self.toggle_word_active).pack(side=tk.LEFT)

        # Word List
        self.word_list = tk.Listbox(right_frame, bg="#23272A", fg="#FFFFFF", selectbackground="#7289DA")
        self.word_list.pack(fill=tk.BOTH, expand=True)

        # Control (Interval, Start Noti, Import feature)
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        ttk.Label(control_frame, text="Notification Interval (minutes):").pack(anchor='w', pady=(0, 5))
        self.interval_entry = ttk.Entry(control_frame, width=5)
        self.interval_entry.insert(tk.END, "1")
        self.interval_entry.pack(anchor='w', pady=(0, 5))

        ttk.Button(control_frame, text="Set Interval", command=self.set_interval).pack(fill=tk.X, pady=(0, 5))
        self.toggle_button = ttk.Button(control_frame, text="Start Notifications", command=self.toggle_notifications)
        self.toggle_button.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(control_frame, text="Import CSV", command=self.import_csv).pack(fill=tk.X, pady=(0, 5))

    # Adds group to list of groups
    def add_group(self):
        group_name = self.group_entry.get()
        self.word_manager.add_group(group_name)
        self.group_entry.delete(0, tk.END)
        self.load_groups()

    # Deletes a group from list of group
    # Does not delete more than one and only deletes selected from cursor
    def delete_group(self):
        selected = self.group_list.curselection()
        if selected:
            group_name = self.group_list.get(selected[0])
            self.word_manager.delete_group(group_name)
            self.load_groups()
            self.word_list.delete(0, tk.END)

    # Toggles selected group for active notification cycling
    # Loops through all of the group names and toggles the matching group name
    # Add validation later to prevent duplicate group names
    def toggle_group_active(self):
        selected = self.group_list.curselection()
        if selected:
            group_name = self.group_list.get(selected[0])
            group = next((g for g in self.word_manager.get_groups() if g.name == group_name), None)
            if group:
                self.word_manager.set_group_active(group_name, not group.active)
                self.load_groups()

    # Adds a word to a group
    def add_word(self):
        group_name = self.group_entry.get()
        word = self.word_entry.get()
        definition = self.definition_entry.get()
        self.word_manager.add_vocab(group_name, word, definition)
        self.word_entry.delete(0, tk.END)
        self.definition_entry.delete(0, tk.END)
        self.load_words()

    # Removes a selected word from it's group and deletes it 
    def delete_word(self):
        selected = self.word_list.curselection()
        if selected:
            word_info = self.word_list.get(selected[0])
            word = word_info.split(":")[0].strip()
            group_name = self.group_entry.get()
            self.word_manager.delete_vocab(group_name, word)
            self.load_words()

    # Toggles a word active
    # Loops through a groups list of words and finds its match
    def toggle_word_active(self):
        selected = self.word_list.curselection()
        if selected:
            word_info = self.word_list.get(selected[0])
            word = word_info.split(":")[0].strip()
            group_name = self.group_entry.get()
            vocab = next((v for v in self.word_manager.get_vocab_list(group_name) if v.word == word), None)
            if vocab:
                self.word_manager.set_vocab_active(group_name, word, not vocab.active)
                self.load_words()

    # Selecting a group loads it into 
    def select_group(self, event):
        selected = self.group_list.curselection()
        if selected:
            group_name = self.group_list.get(selected[0])
            self.group_entry.delete(0, tk.END)
            self.group_entry.insert(0, group_name)
            self.load_words()

    # Grabs the list of groups using word_manager and loads into group_list
    # Also sets the color of groups based off active status
    def load_groups(self):
        self.group_list.delete(0, tk.END)
        groups = self.word_manager.get_groups()
        for group in groups:
            self.group_list.insert(tk.END, group.name)
            if not group.active:
                self.group_list.itemconfig(tk.END, fg="gray")

    # Loads words into word_list
    # Sets color of words based off active status
    def load_words(self):
        self.word_list.delete(0, tk.END)
        group_name = self.group_entry.get()
        vocab_list = self.word_manager.get_vocab_list(group_name)
        for vocab in vocab_list:
            self.word_list.insert(tk.END, f"{vocab.word}: {vocab.definition}")
            if not vocab.active:
                self.word_list.itemconfig(tk.END, fg="gray")

    # Uses the interval widget to set the current interval of the noticiation thread/timer
    def set_interval(self):
        try:
            interval_minutes = int(self.interval_entry.get())
            self.interval = interval_minutes * 60  # convert minutes to seconds
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the interval.")

    # Starts and stops the notification thread 
    def toggle_notifications(self):
        if not self.notification_thread or not self.notification_thread.is_alive():
            self.notification_stop_event.clear()
            self.notification_thread = threading.Thread(target=self.display_notifications, daemon=True)
            self.notification_thread.start()
            self.toggle_button.config(text="Pause Notifications")
        else:
            self.notification_stop_event.set()
            self.toggle_button.config(text="Resume Notifications")

    # Checks to see if the notification thread is off and if it isn't, loops through
    # active groups and words and displays a toast
    def display_notifications(self):
        while not self.notification_stop_event.is_set():
            groups = self.word_manager.get_groups()
            for group in groups:
                if group.active:
                    vocab_list = group.vocab_list
                    for vocab in vocab_list:
                        if vocab.active:
                            if self.notification_stop_event.is_set():
                                return
                            self.toaster.show_toast(vocab.word, vocab.definition, icon_path="icon.ico", duration=3)
                            self.wait_with_check(self.interval)

    def wait_with_check(self, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            if self.notification_stop_event.is_set():
                return
            time.sleep(0.1)  # Check every 100ms

    # Uses the import function from word_manager to load a CSV file from explorer
    # and populate a group and word list with the contents of the CSV
    # Several limitations
    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            # Check for an entered group name first 
            group_name = self.group_entry.get()
            if not group_name:
                messagebox.showerror("Error", "Please enter a group name.")
                return
            if not any(group.name == group_name for group in self.word_manager.get_groups()):
                self.word_manager.add_group(group_name)
            self.word_manager.import_vocab_from_csv(group_name, file_path)
            self.load_groups()
            self.load_words()

    # Minimizes the application to the system tray 
    def hide_window(self):
        self.withdraw()
        image = Image.open("icon.ico")
        menu = (item('Show', self.show_window), item('Quit', self.quit))
        self.tray_icon = pystray.Icon("platinum", image, "Platinum", menu)
        self.tray_icon.run()

    # Pulls the GUI back into screen
    def show_window(self):
        self.deiconify()
        self.tray_icon.stop()

    # Closes both the application and stops the notification thread
    def quit(self):
        if self.notification_thread and self.notification_thread.is_alive():
            self.notification_stop_event.set()
            self.notification_thread.join(timeout=1)  # Wait for up to 1 second
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        sys.exit()
