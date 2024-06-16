import json
import csv
from tkinter import messagebox

class Vocab:
    def __init__(self, word, definition, active=True):
        self.word = word
        self.definition = definition
        self.active = active

class Group:
    def __init__(self, name, vocab_list=None, active=True):
        self.name = name
        self.vocab_list = vocab_list or []
        self.active = active

class WordManager:
    def __init__(self):
        self.groups_file = "groups.json"
        self.groups = self.load_groups()

    def load_groups(self):
        try:
            with open(self.groups_file, "r") as file:
                group_data = json.load(file)
                groups = []
                for group in group_data:
                    vocab_list = [Vocab(vocab["word"], vocab["definition"], vocab["active"]) for vocab in group["vocab_list"]]
                    groups.append(Group(group["name"], vocab_list, group["active"]))
                return groups
        except FileNotFoundError:
            return []

    def save_groups(self):
        group_data = []
        for group in self.groups:
            vocab_data = [{"word": vocab.word, "definition": vocab.definition, "active": vocab.active} for vocab in group.vocab_list]
            group_data.append({"name": group.name, "vocab_list": vocab_data, "active": group.active})
        with open(self.groups_file, "w") as file:
            json.dump(group_data, file)

    def add_group(self, group_name):
        if not any(group.name == group_name for group in self.groups):
            self.groups.append(Group(group_name))
            self.save_groups()

    def delete_group(self, group_name):
        self.groups = [group for group in self.groups if group.name != group_name]
        self.save_groups()

    def add_vocab(self, group_name, word, definition):
        for group in self.groups:
            if group.name == group_name:
                if not any(vocab.word == word for vocab in group.vocab_list):
                    group.vocab_list.append(Vocab(word, definition))
                    self.save_groups()
                break

    # import csv from file
    def import_vocab_from_csv(self, group_name, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) >= 2:
                        word = row[0].strip()
                        definition = row[1].strip()
                        self.add_vocab(group_name, word, definition)
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_vocab(self, group_name, word):
        for group in self.groups:
            if group.name == group_name:
                group.vocab_list = [vocab for vocab in group.vocab_list if vocab.word != word]
                self.save_groups()
                break

    def get_groups(self):
        return self.groups

    def get_vocab_list(self, group_name):
        for group in self.groups:
            if group.name == group_name:
                return group.vocab_list
        return []

    def set_group_active(self, group_name, active):
        for group in self.groups:
            if group.name == group_name:
                group.active = active
                self.save_groups()
                break

    def set_vocab_active(self, group_name, word, active):
        for group in self.groups:
            if group.name == group_name:
                for vocab in group.vocab_list:
                    if vocab.word == word:
                        vocab.active = active
                        self.save_groups()
                        break
                break
