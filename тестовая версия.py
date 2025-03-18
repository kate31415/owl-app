import customtkinter
from Dict import Dict, Learning
import json
import os
import webbrowser
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.progress = {}
        self.dictionary = {}

    def add_word(self, word, definition="", example=""):
        if word not in self.progress:
            self.progress[word] = 0
        self.progress[word] += 1

        if word not in self.dictionary:
            self.dictionary[word] = {"definition": definition, "example": example}

    def get_progress(self):
        return self.progress


class Dict:
    def __init__(self):
        self.base_url = "https://dictionary.cambridge.org/ru/"

    def fetch_word_info(self, word):
        url = f"{self.base_url}dictionary/english/{word}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            definition_tag = soup.find("div", class_="def ddef_d db")
            definition = definition_tag.text.strip() if definition_tag else "Определение не найдено"

            example_tag = soup.find("span", class_="eg deg")
            example = example_tag.text.strip() if example_tag else "Пример не найден"

            transcription_tag = soup.find("span", class_="ipa dipa lpr-2 lpl-1")
            transcription = transcription_tag.text.strip() if transcription_tag else "Транскрипция не найдена"

            translation_tag = soup.find("span", class_="trans dtrans")
            translation = translation_tag.text.strip() if translation_tag else "Перевод не найден"

            with open(f"{word}_page.html", "w", encoding="utf-8") as file:
                file.write(response.text)

            return {
                "definition": definition,
                "example": example,
                "transcription": transcription,
                "translation": translation,
            }
        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return {
                "definition": "Ошибка",
                "example": "",
                "transcription": "",
                "translation": "",
            }


class Learning:
    def __init__(self):
        self.dict = Dict()

    def view_word_page(self, word):
        try:
            html_file = f"{word}_page.html"
            if os.path.exists(html_file):
                webbrowser.open(html_file)
            else:
                print("Страница слова не найдена.")
        except Exception as e:
            print(f"Ошибка при открытии страницы: {e}")

    def add_word_from_dict(self, app_instance, word):
        word_info = self.dict.fetch_word_info(word)
        definition = word_info["definition"]
        example = word_info["example"]
        transcription = word_info["transcription"]
        translation = word_info["translation"]

        app_instance.current_user.add_word(word, definition, example)
        app_instance.tracker.save_data()

        app_instance.show_message(
            f"Слово '{word}' добавлено!\n"
            f"Определение: {definition}\n"
            f"Транскрипция: {transcription}\n"
            f"Перевод: {translation}\n"
            f"Пример: {example}"
        )


class ProgressTracker:
    def __init__(self, data_file="users.json"):
        self.data_file = data_file
        self.users = {}
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


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Green Owl - Изучение языков")
        self.geometry("800x600")

        self.tracker = ProgressTracker()
        self.current_user = None
        self.learning = Learning()

        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()

        label = customtkinter.CTkLabel(self, text="Green Owl", font=("Arial", 24))
        label.pack(pady=20)

        register_button = customtkinter.CTkButton(self, text="Регистрация", command=self.register)
        register_button.pack(pady=10)

        login_button = customtkinter.CTkButton(self, text="Авторизация", command=self.login)
        login_button.pack(pady=10)

        exit_button = customtkinter.CTkButton(self, text="Выход", command=self.quit)
        exit_button.pack(pady=10)

    def register(self):
        self.clear_window()

        label = customtkinter.CTkLabel(self, text="Регистрация", font=("Arial", 20))
        label.pack(pady=10)

        username_entry = customtkinter.CTkEntry(self, placeholder_text="Имя пользователя")
        username_entry.pack(pady=5)

        password_entry = customtkinter.CTkEntry(self, placeholder_text="Пароль", show="*")
        password_entry.pack(pady=5)

        def handle_register():
            username = username_entry.get()
            password = password_entry.get()
            if self.tracker.register_user(username, password):
                self.show_message("Регистрация успешна!")
                self.create_main_menu()
            else:
                self.show_message("Пользователь уже существует.")

        register_button = customtkinter.CTkButton(self, text="Зарегистрироваться", command=handle_register)
        register_button.pack(pady=10)

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.create_main_menu)
        back_button.pack(pady=10)

    def login(self):
        self.clear_window()

        label = customtkinter.CTkLabel(self, text="Авторизация", font=("Arial", 20))
        label.pack(pady=10)

        username_entry = customtkinter.CTkEntry(self, placeholder_text="Имя пользователя")
        username_entry.pack(pady=5)

        password_entry = customtkinter.CTkEntry(self, placeholder_text="Пароль", show="*")
        password_entry.pack(pady=5)

        def handle_login():
            username = username_entry.get()
            password = password_entry.get()
            user = self.tracker.authenticate(username, password)
            if user:
                self.current_user = user
                self.user_menu()
            else:
                self.show_message("Неверное имя пользователя или пароль.")

        login_button = customtkinter.CTkButton(self, text="Войти", command=handle_login)
        login_button.pack(pady=10)

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.create_main_menu)
        back_button.pack(pady=10)

    def user_menu(self):
        self.clear_window()

        label = customtkinter.CTkLabel(self, text=f"Добро пожаловать, {self.current_user.username}!", font=("Arial", 20))
        label.pack(pady=10)

        add_word_button = customtkinter.CTkButton(self, text="Добавить слово", command=self.add_word_from_dict_ui)
        add_word_button.pack(pady=5)

        view_progress_button = customtkinter.CTkButton(self, text="Просмотреть прогресс", command=self.view_progress)
        view_progress_button.pack(pady=5)

        logout_button = customtkinter.CTkButton(self, text="Выйти", command=self.logout)
        logout_button.pack(pady=5)

    def add_word_from_dict_ui(self):
        self.clear_window()
        new_window = customtkinter.CTkToplevel()
        label = customtkinter.CTkLabel(self, text="Добавить слово из словаря", font=("Arial", 20))
        label.pack(pady=10)

        word_entry = customtkinter.CTkEntry(self, placeholder_text="Введите слово")
        word_entry.pack(pady=5)

        def handle_add_word():
            word = word_entry.get().strip().lower()
            if word:
                self.learning.add_word_from_dict(self, word)

        add_button = customtkinter.CTkButton(self, text="Добавить", command=handle_add_word)
        add_button.pack(pady=10)

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.user_menu)
        back_button.pack(pady=10)

    def view_progress(self):
        self.clear_window()

        progress = self.current_user.get_progress()
        if not progress:
            self.show_message("Прогресс пуст.")
            self.user_menu()
            return

        label = customtkinter.CTkLabel(self, text="Ваш прогресс:", font=("Arial", 20))
        label.pack(pady=10)

        textbox = customtkinter.CTkTextbox(self, wrap="word", height=300)
        textbox.pack(pady=10, padx=10, fill="both", expand=True)

        for word, count in progress.items():
            word_info = self.current_user.dictionary.get(word, {"definition": "Слово не найдено", "example": ""})
            definition = word_info["definition"]
            example = word_info["example"]
            textbox.insert("end", f"{word}: {count} повторений\nОпределение: {definition}\nПример: {example}\n\n")
        textbox.configure(state="disabled")

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.user_menu)
        back_button.pack(pady=10)

    def logout(self):
        self.current_user = None
        self.create_main_menu()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_message(self, message):
        label = customtkinter.CTkLabel(self, text=message, font=("Arial", 14))
        label.pack(pady=10)


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("green")
    app = App()
    app.mainloop()