import json
import os
import logging
from UserStats import UserStats

logging.basicConfig(filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.progress = {}  # Прогресс пользователя по каждому слову
        self.dictionary = {}  # Словарь пользователя

    def add_word(self, word, definition="", example="", transcription="", translation=""):
        """Добавляем слово в словарь и увеличиваем прогресс."""
        # Добавляем слово в прогресс, если его нет
        if word not in self.progress:
            self.progress[word] = 0
        self.progress[word] += 1
        
        # Добавляем слово в словарь пользователя
        if word not in self.dictionary:
            self.dictionary[word] = {
                "definition": definition,
                "example": example,
                "transcription": transcription,
                "translation": translation
            }

    def get_progress(self):
        """Получаем прогресс по всем словам пользователя."""
        return self.progress

    def get_word_info(self, word):
        """Получаем информацию о слове."""
        return self.dictionary.get(word, {"definition": "Слово не найдено", "example": "", "transcription": "", "translation": ""})

class ProgressTracker:
    def __init__(self, data_file="users.json"):
        self.data_file = data_file
        self.users = {}
        self.user_stats = UserStats()
        self.load_data()

    def load_data(self):
        """Загружаем данные пользователей из файла."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                data = json.load(file)
                for username, user_data in data.items():
                    # Создаем объект User для каждого пользователя
                    user = User(username, user_data["password"])
                    user.progress = user_data.get("progress", {})
                    user.dictionary = user_data.get("dictionary", {})
                    self.users[username] = user

    def save_data(self):
        """Сохраняем данные пользователей в файл."""
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
        """Регистрируем нового пользователя."""
        if username in self.users:
            return False  # Пользователь уже существует
        self.users[username] = User(username, password)
        self.save_data()
        logger.info(f"Новый пользователь зарегистрирован: {username}")
        return True

    def authenticate(self, username, password):
        """Аутентификация пользователя по имени и паролю."""
        user = self.users.get(username)
        if user and user.password == password:
            logger.info(f"Пользователь вошёл: {username}")
            return user
        logger.warning(f"Ошибка авторизации: {username}")
        return None

    def autosave(self):
        """Автосохранение данных пользователей."""
        self.save_data()
        logger.info("Автосохранение данных выполнено.")

    def update_study_time(self, username, study_duration):
        """Обновляем время обучения для пользователя."""
        self.user_stats.update_study_time(username, study_duration)

    def get_user_stats(self, username):
        """Получаем статистику пользователя."""
        return self.user_stats.get_user_stats(username)

    def add_word_for_user(self, username, word, definition="", example="", transcription="", translation=""):
        """Добавляем слово для авторизованного пользователя."""
        user = self.users.get(username)
        if user:
            user.add_word(word, definition, example, transcription, translation)
            self.save_data()  # Сохраняем данные в файл
            return f"Слово '{word}' добавлено успешно!"
        return "Пользователь не найден!"

    def get_user_words(self, username):
        """Получаем все слова пользователя."""
        user = self.users.get(username)
        if user:
            return user.dictionary
        return "Пользователь не найден!"