import json

class WordManager:
    def __init__(self):
        self.words_file = "words.json"
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

    def add_word(self, word):
        self.words.append(word)
        self.save_words()

    def delete_word(self, word):
        if word in self.words:
            self.words.remove(word)
        if word in self.noti_words:
            self.noti_words.remove(word)
        self.save_words()

    def get_words(self):
        return self.words

    def load_noti_words(self):
        try:
            with open(self.words_file, "r") as file:
                data = json.load(file)
                if "noti_words" in data:
                    return data["noti_words"]
                else:
                    return []
        except FileNotFoundError:
            return []

    def save_noti_words(self):
        try:
            with open(self.words_file, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        data["noti_words"] = self.noti_words
        with open(self.words_file, "w") as file:
            json.dump(data, file)

    def add_to_noti_words(self, word):
        if word not in self.noti_words:
            self.noti_words.append(word)
        self.save_noti_words()
        return self.words
