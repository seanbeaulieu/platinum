import json

class WordManager:
    def __init__(self):
        self.words_file = "words.json"
        self.noti_words_file = "noti_words.json"
        self.words = self.load_words()
        self.noti_words = self.load_noti_words()

    def load_words(self):
        try:
            with open(self.words_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_words(self):
        with open(self.words_file, "w") as file:
            json.dump(self.words, file)

    # storing words as a dictionary
    def add_word(self, word, definition):
        if word not in self.words:
            self.words[word] = definition
            self.save_words()

    def delete_word(self, word):
        if word in self.words:
            self.words.remove(word)
            self.save_words()
        if word in self.noti_words:
            self.noti_words.remove(word)
            self.save_noti_words()

    def get_words(self):
        return self.words

    def load_noti_words(self):
        try:
            with open(self.noti_words_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_noti_words(self):
        with open(self.noti_words_file, "w") as file:
            json.dump(self.noti_words, file)

    def add_to_noti_words(self, word, definition):
        if word not in self.noti_words:
            self.noti_words[word] = definition
            self.save_noti_words()

    def remove_from_noti_words(self, word):
        if word in self.noti_words:
            self.noti_words.remove(word)
            self.save_noti_words()

    def get_noti_words(self):
        return self.noti_words
