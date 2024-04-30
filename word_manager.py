import json

class WordManager:
    def __init__(self):
        self.words_file = "words.json"
        self.words = self.load_words()

    def load_words(self):
        try:
            with open(self.words_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_words(self):
        with open(self.words_file, "w") as file:
            json.dump(self.words, file)

    def add_word(self, word):
        self.words.append(word)
        self.save_words()

    def get_words(self):
        return self.words
