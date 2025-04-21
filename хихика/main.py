import customtkinter as ctk
from Dict import Dict, Learning
from User import User, ProgressTracker
from UserStats import UserStats
from gamessss import GamesPanel

import json
import os
import textwrap
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import logging
import random

logging.basicConfig(filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class UserStatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Статистика пользователей")
        self.tracker = ProgressTracker()
        self.create_widgets()

    def create_widgets(self):
        # Поле для ввода имени пользователя
        tk.Label(self.root, text="Имя пользователя:").grid(row=0, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        # Кнопка для получения статистики
        tk.Button(self.root, text="Показать статистику", command=self.show_user_stats).grid(row=0, column=2, padx=10, pady=5)

        # Таблица для отображения данных
        columns = ("Параметр", "Значение")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("Параметр", text="Параметр")
        self.tree.heading("Значение", text="Значение")
        self.tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def show_user_stats(self):
        # Очистка таблицы перед обновлением
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получение имени пользователя
        username = self.username_entry.get()
        if not username:
            self.tree.insert("", "end", values=("Ошибка", "Введите имя пользователя"))
            return

        # Получение статистики пользователя из ProgressTracker
        stats = self.tracker.get_user_stats(username)

        # Отображение данных в таблице
        self.tree.insert("", "end", values=("Общее время обучения (сек)", stats["total_study_time"]))
        self.tree.insert("", "end", values=("Количество дней подряд", stats["streak_days"]))
        self.tree.insert("", "end", values=("Последняя дата обучения", stats["last_study_date"]))
        self.tree.insert("", "end", values=("Награды", ", ".join(map(str, stats["rewards"]))))
        self.tree.insert("", "end", values=("Слова", ", ".join(stats["words"])))

        # Автоматическое расширение столбцов
        self.tree.column("Параметр", width=200, stretch=True)
        self.tree.column("Значение", width=400, stretch=True)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Green Owl - Изучение языков")
        self.geometry("500x500")
        self.tracker = ProgressTracker()
        self.current_user = None
        self.learning = Learning()

        # Выбор темы
        self.theme_var = tk.StringVar()
        themes_list = list(self.learning.themes.keys()) or ["еда"]  # запасной вариант
        self.theme_var.set(themes_list[0])

        self.theme_menu = ctk.CTkOptionMenu(self, variable=self.theme_var, values=themes_list)
        self.theme_menu.pack(pady=5)

        # Выбор источника для игры
        self.game_source_var = tk.StringVar(value="Изученные слова")  # по умолчанию из изученных слов

        self.game_source_frame = ctk.CTkFrame(self)
        self.game_source_frame.pack(pady=10)

        self.radio_button_study = ctk.CTkRadioButton(self.game_source_frame, text="Изученные слова", variable=self.game_source_var, value="Изученные слова")
        self.radio_button_study.pack(side=tk.LEFT, padx=10)

        self.radio_button_themes = ctk.CTkRadioButton(self.game_source_frame, text="Темы", variable=self.game_source_var, value="Темы")
        self.radio_button_themes.pack(side=tk.LEFT, padx=10)

        self.game_btn = ctk.CTkButton(self, text="Играть", command=self.start_game)
        self.game_btn.pack(pady=5)

        # self.check_btn = ctk.CTkButton(self, text="Проверить ответ", command=self.check_answer)
        # self.check_btn.pack(pady=5)

        self.game_output = ctk.CTkTextbox(self, width=600, height=100)
        self.game_output.pack(pady=10)

        self.current_word = None
        self.correct_answer = None

        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()
        label = ctk.CTkLabel(self, text="Green Owl", font=("Arial", 24))
        label.pack(pady=10)
        register_button = ctk.CTkButton(self, text="Регистрация", command=self.register)
        register_button.pack(pady=5)
        login_button = ctk.CTkButton(self, text="Авторизация", command=self.login)
        login_button.pack(pady=5)
        exit_button = ctk.CTkButton(self, text="Выход", command=self.quit)
        exit_button.pack(pady=5)

    def register(self):
        self.clear_window()
        label = ctk.CTkLabel(self, text="Регистрация", font=("Arial", 20))
        label.pack(pady=10)
        username_entry = ctk.CTkEntry(self, placeholder_text="Имя пользователя")
        username_entry.pack(pady=5)
        password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        password_entry.pack(pady=5)

        def handle_register():
            username = username_entry.get()
            password = password_entry.get()
            if self.tracker.register_user(username, password):
                messagebox.showinfo("Успешно", "Регистрация успешна!")
                self.create_main_menu()
            else:
                messagebox.showerror("Ошибка", "Пользователь уже существует.")

        register_button = ctk.CTkButton(self, text="Зарегистрироваться", command=handle_register)
        register_button.pack(pady=10)
        back_button = ctk.CTkButton(self, text="Назад", command=self.create_main_menu)
        back_button.pack(pady=5)

    def login(self):
        self.clear_window()
        label = ctk.CTkLabel(self, text="Авторизация", font=("Arial", 20))
        label.pack(pady=10)
        username_entry = ctk.CTkEntry(self, placeholder_text="Имя пользователя")
        username_entry.pack(pady=5)
        password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        password_entry.pack(pady=5)

        def handle_login():
            username = username_entry.get()
            password = password_entry.get()
            user = self.tracker.authenticate(username, password)
            if user:
                self.current_user = user
                self.user_menu()
            else:
                messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

        login_button = ctk.CTkButton(self, text="Войти", command=handle_login)
        login_button.pack(pady=10)
        back_button = ctk.CTkButton(self, text="Назад", command=self.create_main_menu)
        back_button.pack(pady=5)

    def user_menu(self):
        self.clear_window()
        label = ctk.CTkLabel(self, text=f"Добро пожаловать, {self.current_user.username}!", font=("Arial", 20))
        label.pack(pady=10)
        add_word_button = ctk.CTkButton(self, text="Добавить слово", command=self.add_word_from_dict_ui)
        add_word_button.pack(pady=5)
        view_progress_button = ctk.CTkButton(self, text="Список слов", command=self.view_progress_ui)
        view_progress_button.pack(pady=5)
        show_chart_button = ctk.CTkButton(self, text="Показать график прогресса", command=self.show_progress_chart)
        show_chart_button.pack(pady=5)
        show_chart_button = ctk.CTkButton(self, text="Информация о прогрессе", command=self.show_user_stats)
        show_chart_button.pack(pady=5)
        play_games_button = ctk.CTkButton(self, text="Игры со словами", command=lambda: GamesPanel(self, self.current_user, self.learning))
        play_games_button.pack(pady=5)
        logout_button = ctk.CTkButton(self, text="Выйти", command=self.logout)
        logout_button.pack(pady=5)

    def show_user_stats(self):
        # Создание нового окна для статистики пользователя
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Статистика пользователя")
        stats_window.geometry("500x400")
        
        # Открытие окна с информацией о прогрессе
        user_stats_app = UserStatsApp(stats_window)
        
        stats_window.mainloop()

    def add_word_from_dict_ui(self):
        add_word_window = ctk.CTkToplevel(self)
        add_word_window.title("Добавить слово")
        add_word_window.geometry("400x400")
        label = ctk.CTkLabel(add_word_window, text="Добавить слово из словаря", font=("Arial", 20))
        label.pack(pady=10)
        word_entry = ctk.CTkEntry(add_word_window, placeholder_text="Введите слово")
        word_entry.pack(pady=5)



        def handle_add_word():
            word = word_entry.get().strip().lower()
            if word:
                start_time = datetime.datetime.now()
                word_info = self.learning.add_word(word)
                end_time = datetime.datetime.now()
                study_duration = (end_time - start_time).seconds
                self.tracker.update_study_time(self.current_user.username, study_duration)
                if word_info:
                    self.current_user.add_word(
                        word,
                        definition="",  # Предполагается, что определение не используется
                        example=word_info.get("example", ""),
                        transcription=word_info.get("transcription", ""),
                        translation=word_info.get("translation", "")
                    )
                    self.tracker.save_data()
                    messagebox.showinfo("Успешно", f"Слово '{word}' добавлено!")
                    reward_message = self.tracker.user_stats.check_rewards(self.current_user.username)
                    if reward_message:
                        messagebox.showinfo("Награда", reward_message)
                else:
                    messagebox.showerror("Ошибка", f"Слово '{word}' не найдено.")
                add_word_window.destroy()
                self.user_menu()
            else:
                messagebox.showerror("Ошибка", "Введите слово.")

        add_button = ctk.CTkButton(add_word_window, text="Добавить", command=handle_add_word)
        add_button.pack(pady=10)
        back_button = ctk.CTkButton(add_word_window, text="Назад", command=add_word_window.destroy)
        back_button.pack(pady=10)

    def view_progress_ui(self):
        progress_window = ctk.CTkToplevel(self)
        progress_window.title("Прогресс")
        progress_window.geometry("800x600")
        label = ctk.CTkLabel(progress_window, text="Ваш прогресс:", font=("Arial", 20))
        label.pack(pady=10)
        search_frame = ctk.CTkFrame(progress_window)
        search_frame.pack(pady=10, padx=10, fill="x")
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Поиск слова")
        search_entry.pack(side="left", padx=10, fill="x", expand=True)
        search_button = ctk.CTkButton(search_frame, text="Поиск", command=lambda: search_words(search_entry.get()))
        search_button.pack(side="right", padx=10)
        words_frame = ctk.CTkScrollableFrame(progress_window)
        words_frame.pack(pady=10, padx=10, fill="both", expand=True)

        def search_words(query):
            words_frame._parent_canvas.yview_moveto(0)
            for widget in words_frame.winfo_children():
                widget.destroy()
            if not query:
                display_words()
            else:
                filtered_words = {word: info for word, info in self.current_user.dictionary.items() if query.lower() in word.lower()}
                if not filtered_words:
                    label = ctk.CTkLabel(words_frame, text="Слова не найдены", font=("Arial", 14))
                    label.pack(pady=10)
                else:
                    for idx, (word, info) in enumerate(filtered_words.items(), start=1):
                        word_button = ctk.CTkButton(words_frame, text=f"{idx}. {word}", command=lambda w=word: self.show_word_info(w))
                        word_button.pack(pady=5, fill="x")

        def display_words():
            for widget in words_frame.winfo_children():
                widget.destroy()
            if not self.current_user.dictionary:
                label = ctk.CTkLabel(words_frame, text="Библиотека слов пуста", font=("Arial", 14))
                label.pack(pady=10)
            else:
                for idx, (word, info) in enumerate(self.current_user.dictionary.items(), start=1):
                    word_button = ctk.CTkButton(words_frame, text=f"{idx}. {word}", command=lambda w=word: self.show_word_info(w))
                    word_button.pack(pady=5, fill="x")

        display_words()
        back_button = ctk.CTkButton(progress_window, text="Назад", command=progress_window.destroy)
        back_button.pack(pady=10)

    def show_word_info(self, word):
        word_info_window = ctk.CTkToplevel(self)
        word_info_window.title(f"Информация о слове: {word}")
        word_info_window.geometry("500x500")
        word_info = self.current_user.get_word_info(word)
        definition = word_info["definition"]
        example = word_info["example"]
        transcription = word_info["transcription"]
        translation = word_info["translation"]

        label = ctk.CTkLabel(word_info_window, text=f"Слово: {word}", font=("Arial", 20))
        label.pack(pady=10)

        if example == "Слово не найдено":
            error_label = ctk.CTkLabel(word_info_window, text="Слово не найдено в словаре.", font=("Arial", 14), text_color="red")
            error_label.pack(pady=5)
        else:
            translation_label = ctk.CTkLabel(word_info_window, text=textwrap.fill(f"Перевод: {translation}", width=50), font=("Arial", 14))
            translation_label.pack(pady=5)

            transcription_label = ctk.CTkLabel(word_info_window, text=f"Транскрипция: {transcription}", font=("Arial", 14))
            transcription_label.pack(pady=5)

            example_label = ctk.CTkLabel(word_info_window, text=textwrap.fill(f"Пример: {example}", width=50), font=("Arial", 14))
            example_label.pack(pady=5)

        back_button = ctk.CTkButton(word_info_window, text="Назад", command=word_info_window.destroy)
        back_button.pack(pady=10)

    def start_game(self):
        # Проверяем, что выбрал пользователь
        game_source = self.game_source_var.get()

        # Если выбран источник "Изученные слова"
        if game_source == "Изученные слова":
            words = self.learning.get_progress_data()

        # Если выбран источник "Темы"
        elif game_source == "Темы":
            theme_name = self.theme_var.get()
            words = self.learning.get_words_by_theme(theme_name)

        # Если нет слов в выбранном источнике
        if not words:
            self.game_output.delete("1.0", "end")
            self.game_output.insert("1.0", "Нет доступных слов для игры!")
            return

        # Выбираем случайное слово из списка
        word = random.choice(list(words.keys()))

        # Если это изученное слово, то получаем правильный ответ через словарь
        if game_source == "Изученные слова":
            self.correct_answer = words[word]["translation"]
        else:
            # Если это слово из темы, то предполагаем, что правильный ответ - само слово
            self.correct_answer = words[word]

        self.current_word = word

        self.game_output.delete("1.0", "end")
        self.game_output.insert("1.0", f"Переведите слово: {word}\nВведите перевод и нажмите 'Проверить ответ'")

    def show_progress_chart(self):
        progress_window = ctk.CTkToplevel(self)
        progress_window.title("График прогресса")
        progress_window.geometry("800x600")
        progress = self.current_user.get_progress()
        if not progress:
            messagebox.showinfo("Информация", "Нет данных для отображения.")
            progress_window.destroy()
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
        canvas = FigureCanvasTkAgg(fig, master=progress_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill="both", expand=True)
        back_button = ctk.CTkButton(progress_window, text="Назад", command=progress_window.destroy)
        back_button.pack(pady=10)

    def logout(self):
        self.current_user = None
        self.create_main_menu()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_message(self, message):
        messagebox.showinfo("Сообщение", message)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("green")
    app = App()
    app.mainloop()