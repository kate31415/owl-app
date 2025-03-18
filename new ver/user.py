import json
import os
from UserStats import UserStats

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.progress = {}
        self.dictionary = {}

    def add_word(self, word, definition="", example="", transcription="", translation=""):
        if word not in self.progress:
            self.progress[word] = 0
        self.progress[word] += 1
        if word not in self.dictionary:
            self.dictionary[word] = {
                "definition": definition,
                "example": example,
                "transcription": transcription,
                "translation": translation
            }

    def get_progress(self):
        return self.progress

    def get_word_info(self, word):
        return self.dictionary.get(word, {"definition": "Слово не найдено", "example": "", "transcription": "", "translation": ""})

class ProgressTracker:
    def __init__(self, data_file="users.json"):
        self.data_file = data_file
        self.users = {}
        self.user_stats = UserStats()
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                for username, user_data in data.items():
                    user = User(username, user_data["password"])
                    user.progress = user_data.get("progress", {})
                    user.dictionary = user_data.get("dictionary", {})
                    self.users[username] = user

    def save_data(self):
        data = {
            username: {
                "password": user.password,
                "progress": user.progress,
                "dictionary": user.dictionary,
            }
            for username, user in self.users.items()
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=4)

    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        self.save_data()
        return True

    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return user
        return None

    def update_study_time(self, username, study_duration):
        self.user_stats.update_study_time(username, study_duration)

    def get_user_stats(self, username):
        return self.user_stats.get_user_stats(username)