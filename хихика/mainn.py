import customtkinter
from tkinter import messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime
import json
import os
import logging

# Настройка логгера
logging.basicConfig(filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- МОДЕЛИ ------------------
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

class UserStats:
    def __init__(self):
        self.data = {}

    def update_study_time(self, username, study_duration):
        user_stats = self.data.setdefault(username, {"total_study_time": 0, "streak_days": 0, "last_study_date": None, "rewards": []})
        today = datetime.date.today()
        last_date = user_stats.get("last_study_date")

        if last_date:
            last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
            if (today - last_date).days == 1:
                user_stats["streak_days"] += 1
            elif (today - last_date).days > 1:
                user_stats["streak_days"] = 1
        else:
            user_stats["streak_days"] = 1

        user_stats["total_study_time"] += study_duration
        user_stats["last_study_date"] = today.strftime("%Y-%m-%d")

        self.check_rewards(username)

    def check_rewards(self, username):
        user_stats = self.data[username]
        rewards = user_stats["rewards"]

        if user_stats["streak_days"] == 3 and "3-day streak" not in rewards:
            rewards.append("3-day streak")
            return "Поздравляем! Вы достигли серии в 3 дня!"
        if user_stats["total_study_time"] > 3600 and "1 час обучения" not in rewards:
            rewards.append("1 час обучения")
            return "Поздравляем! Вы обучались более 1 часа!"
        return None

    def get_user_stats(self, username):
        return self.data.get(username, {"total_study_time": 0, "streak_days": 0, "last_study_date": "-", "rewards": []})

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
            } for username, user in self.users.items()
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file, indent=4)

    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, password)
        self.save_data()
        logger.info(f"Новый пользователь зарегистрирован: {username}")
        return True

    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            logger.info(f"Пользователь вошёл: {username}")
            return user
        logger.warning(f"Ошибка авторизации: {username}")
        return None

    def autosave(self):
        self.save_data()
        logger.info("Автосохранение данных выполнено.")

# ----------------- ИНТЕРФЕЙС ------------------
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Green Owl - Языковое обучение")
        self.geometry("600x500")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.tracker = ProgressTracker()
        self.current_user = None
        self.build_main_menu()

    def build_main_menu(self):
        self.clear_window()
        customtkinter.CTkLabel(self, text="Green Owl", font=("Arial", 24)).pack(pady=10)
        customtkinter.CTkButton(self, text="Регистрация", command=self.register).pack(pady=5)
        customtkinter.CTkButton(self, text="Вход", command=self.login).pack(pady=5)

    def register(self):
        self.clear_window()
        username = customtkinter.CTkEntry(self, placeholder_text="Имя пользователя")
        username.pack(pady=5)
        password = customtkinter.CTkEntry(self, placeholder_text="Пароль", show="*")
        password.pack(pady=5)

        def handle():
            if self.tracker.register_user(username.get(), password.get()):
                messagebox.showinfo("Успех", "Регистрация прошла успешно!")
                self.build_main_menu()
            else:
                messagebox.showerror("Ошибка", "Пользователь уже существует")

        customtkinter.CTkButton(self, text="Зарегистрироваться", command=handle).pack(pady=10)
        customtkinter.CTkButton(self, text="Назад", command=self.build_main_menu).pack()

    def login(self):
        self.clear_window()
        username = customtkinter.CTkEntry(self, placeholder_text="Имя пользователя")
        username.pack(pady=5)
        password = customtkinter.CTkEntry(self, placeholder_text="Пароль", show="*")
        password.pack(pady=5)

        def handle():
            user = self.tracker.authenticate(username.get(), password.get())
            if user:
                self.current_user = user
                self.user_menu()
            else:
                messagebox.showerror("Ошибка", "Неверные данные")

        customtkinter.CTkButton(self, text="Войти", command=handle).pack(pady=10)
        customtkinter.CTkButton(self, text="Назад", command=self.build_main_menu).pack()

    def user_menu(self):
        self.clear_window()
        customtkinter.CTkLabel(self, text=f"Добро пожаловать, {self.current_user.username}!", font=("Arial", 18)).pack(pady=10)
        customtkinter.CTkButton(self, text="Показать график", command=self.show_chart).pack(pady=5)
        customtkinter.CTkButton(self, text="Выйти", command=self.logout).pack(pady=5)

    def show_chart(self):
        window = customtkinter.CTkToplevel(self)
        window.geometry("600x400")
        progress = self.current_user.get_progress()
        if not progress:
            messagebox.showinfo("Нет данных", "Вы ещё не добавили слов")
            return

        fig, ax = plt.subplots()
        ax.bar(progress.keys(), progress.values(), color="green")
        ax.set_title("Прогресс")
        ax.set_ylabel("Повторы")
        plt.xticks(rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def logout(self):
        self.current_user = None
        self.build_main_menu()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def on_closing(self):
        self.tracker.autosave()
        self.destroy()

if __name__ == "__main__":
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("green")
    app = App()
    app.mainloop()