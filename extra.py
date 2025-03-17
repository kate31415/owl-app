import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from App import User

class ProgressTracker:
    def __init__(self, data_file="users.json"):
        self.data_file = data_file
        self.users = {}  # Словарь для хранения всех пользователей
        self.load_data()

    def load_data(self):
        """Загрузка данных пользователей из файла."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                for username, user_data in data.items():
                    user = User(username, user_data["password"])
                    user.progress = user_data.get("progress", {})
                    user.dictionary = user_data.get("dictionary", {})
                    self.users[username] = user

    def save_data(self):
        """Сохранение данных пользователей в файл."""
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
        """Регистрация нового пользователя."""
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        self.save_data()
        return True

    def authenticate(self, username, password):
        """Аутентификация пользователя."""
        user = self.users.get(username)
        if user and user.password == password:
            return user
        return None

