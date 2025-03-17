import json
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter

from Dict import Dict
from extra import ProgressTracker

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.progress = {}  
        self.dictionary = {}  

    def add_word(self, word, definition="", example=""):
        """Добавление нового слова в прогресс."""
        if word not in self.progress:
            self.progress[word] = 0
        self.progress[word] += 1

        if word not in self.dictionary:
            self.dictionary[word] = {"definition": definition, "example": example}

    def get_progress(self):
        """Возвращает текущий прогресс пользователя."""
        return self.progress

    def get_word_info(self, word):
        """Возвращает информацию о слове."""
        return self.dictionary.get(word, {"definition": "Слово не найдено", "example": ""})



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Green Owl - Изучение языков")
        self.geometry("800x600")

        self.tracker = ProgressTracker()
        self.current_user = None
        self.eng_dict = Dict()

        self.create_main_menu()

    def create_main_menu(self):
        """Создание главного меню."""
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
        """Регистрация нового пользователя."""
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
        """Авторизация пользователя."""
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
        """Меню пользователя."""
        self.clear_window()

        label = customtkinter.CTkLabel(self, text=f"Добро пожаловать, {self.current_user.username}!", font=("Arial", 20))
        label.pack(pady=10)

        add_word_button = customtkinter.CTkButton(self, text="Добавить слово", command=self.add_word_from_dict)
        add_word_button.pack(pady=5)

        view_progress_button = customtkinter.CTkButton(self, text="Просмотреть прогресс", command=self.view_progress)
        view_progress_button.pack(pady=5)

        show_chart_button = customtkinter.CTkButton(self, text="Показать диаграмму прогресса", command=self.show_progress_chart)
        show_chart_button.pack(pady=5)

        view_word_page_button = customtkinter.CTkButton(self, text="Просмотреть страницу слова", command=lambda: self.view_word_page(input("Введите слово: ").strip().lower()))
        view_word_page_button.pack(pady=5)

        logout_button = customtkinter.CTkButton(self, text="Выйти", command=self.logout)
        logout_button.pack(pady=5)

    def add_word_from_dict(self):
        """Добавление слова из словаря."""
        self.clear_window()

        label = customtkinter.CTkLabel(self, text="Добавить слово из словаря", font=("Arial", 20))
        label.pack(pady=10)

        word_entry = customtkinter.CTkEntry(self, placeholder_text="Введите слово")
        word_entry.pack(pady=5)

        def handle_add_word():
            word = word_entry.get().strip().lower()
            if word:
                word_info = self.eng_dict.fetch_word_info(word)
                definition = word_info["definition"]
                example = word_info["example"]

                self.current_user.add_word(word, definition, example)
                self.tracker.save_data()

                self.show_message(f"Слово '{word}' добавлено!\nОпределение: {definition}\nПример: {example}")
                self.user_menu()

        add_button = customtkinter.CTkButton(self, text="Добавить", command=handle_add_word)
        add_button.pack(pady=10)

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.user_menu)
        back_button.pack(pady=10)

    def view_progress(self):
        """Просмотр прогресса."""
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
            word_info = self.current_user.get_word_info(word)
            definition = word_info["definition"]
            example = word_info["example"]
            textbox.insert(
                "end",
                f"{word}: {count} повторений\nОпределение: {definition}\nПример: {example}\n\n",
            )
        textbox.configure(state="disabled")

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.user_menu)
        back_button.pack(pady=10)

    def show_progress_chart(self):
        """Отображение диаграммы прогресса."""
        self.clear_window()

        progress = self.current_user.get_progress()
        if not progress:
            self.show_message("Нет данных для отображения.")
            self.user_menu()
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        words = list(progress.keys())
        counts = list(progress.values())
        ax.bar(words, counts, color='skyblue')
        ax.set_xlabel("Слова")
        ax.set_ylabel("Количество повторений")
        ax.set_title("Прогресс изучения слов")
        plt.xticks(rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill="both", expand=True)

        back_button = customtkinter.CTkButton(self, text="Назад", command=self.user_menu)
        back_button.pack(pady=10)

    def logout(self):
        """Выход из аккаунта."""
        self.current_user = None
        self.create_main_menu()

    def clear_window(self):
        """Очистка окна."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_message(self, message):
        """Показать сообщение."""
        label = customtkinter.CTkLabel(self, text=message, font=("Arial", 14))
        label.pack(pady=10)


if __name__ == "__main__":
    customtkinter.set_appearance_mode("System") 
    customtkinter.set_default_color_theme("green") 
    app = App()
    app.mainloop()