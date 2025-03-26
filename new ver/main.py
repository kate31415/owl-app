import customtkinter
from tkinter import messagebox
from user import User, ProgressTracker
from Dict import Dict, Learning
from UserStats import UserStats

import json
import os
import textwrap
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import random
import webbrowser


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Green Owl - Изучение языков")
        self.geometry("500x500")
        self.tracker = ProgressTracker()
        self.current_user = None
        self.learning = Learning()
        self.create_main_menu()

    def create_main_menu(self):
        self.clear_window()
        label = customtkinter.CTkLabel(self, text="Green Owl", font=("Arial", 24))
        label.pack(pady=10)
        register_button = customtkinter.CTkButton(self, text="Регистрация", command=self.register)
        register_button.pack(pady=5)
        login_button = customtkinter.CTkButton(self, text="Авторизация", command=self.login)
        login_button.pack(pady=5)
        exit_button = customtkinter.CTkButton(self, text="Выход", command=self.quit)
        exit_button.pack(pady=5)

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
                messagebox.showinfo("Успешно", "Регистрация успешна!")
                self.create_main_menu()
            else:
                messagebox.showerror("Ошибка", "Пользователь уже существует.")

        register_button = customtkinter.CTkButton(self, text="Зарегистрироваться", command=handle_register)
        register_button.pack(pady=10)
        back_button = customtkinter.CTkButton(self, text="Назад", command=self.create_main_menu)
        back_button.pack(pady=5)

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
                messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль.")

        login_button = customtkinter.CTkButton(self, text="Войти", command=handle_login)
        login_button.pack(pady=10)
        back_button = customtkinter.CTkButton(self, text="Назад", command=self.create_main_menu)
        back_button.pack(pady=5)

    def user_menu(self):
        self.clear_window()
        label = customtkinter.CTkLabel(self, text=f"Добро пожаловать, {self.current_user.username}!", font=("Arial", 20))
        label.pack(pady=10)
        add_word_button = customtkinter.CTkButton(self, text="Добавить слово", command=self.add_word_from_dict_ui)
        add_word_button.pack(pady=5)
        view_progress_button = customtkinter.CTkButton(self, text="Просмотреть прогресс", command=self.view_progress_ui)
        view_progress_button.pack(pady=5)
        show_chart_button = customtkinter.CTkButton(self, text="Показать диаграмму прогресса", command=self.show_progress_chart)
        show_chart_button.pack(pady=5)
        logout_button = customtkinter.CTkButton(self, text="Выйти", command=self.logout)
        logout_button.pack(pady=5)

    def add_word_from_dict_ui(self):
        add_word_window = customtkinter.CTkToplevel(self)
        add_word_window.title("Добавить слово")
        add_word_window.geometry("400x400")
        label = customtkinter.CTkLabel(add_word_window, text="Добавить слово из словаря", font=("Arial", 20))
        label.pack(pady=10)
        word_entry = customtkinter.CTkEntry(add_word_window, placeholder_text="Введите слово")
        word_entry.pack(pady=5)

        def handle_add_word():
            word = word_entry.get().strip().lower()
            if word:
                start_time = datetime.datetime.now()
                word_info = self.learning.add_word_from_dict(word)
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

        add_button = customtkinter.CTkButton(add_word_window, text="Добавить", command=handle_add_word)
        add_button.pack(pady=10)
        back_button = customtkinter.CTkButton(add_word_window, text="Назад", command=add_word_window.destroy)
        back_button.pack(pady=10)

    def view_progress_ui(self):
        progress_window = customtkinter.CTkToplevel(self)
        progress_window.title("Прогресс")
        progress_window.geometry("800x600")
        label = customtkinter.CTkLabel(progress_window, text="Ваш прогресс:", font=("Arial", 20))
        label.pack(pady=10)
        search_frame = customtkinter.CTkFrame(progress_window)
        search_frame.pack(pady=10, padx=10, fill="x")
        search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Поиск слова")
        search_entry.pack(side="left", padx=10, fill="x", expand=True)
        search_button = customtkinter.CTkButton(search_frame, text="Поиск", command=lambda: search_words(search_entry.get()))
        search_button.pack(side="right", padx=10)
        words_frame = customtkinter.CTkScrollableFrame(progress_window)
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
                    label = customtkinter.CTkLabel(words_frame, text="Слова не найдены", font=("Arial", 14))
                    label.pack(pady=10)
                else:
                    for idx, (word, info) in enumerate(filtered_words.items(), start=1):
                        word_button = customtkinter.CTkButton(words_frame, text=f"{idx}. {word}", command=lambda w=word: self.show_word_info(w))
                        word_button.pack(pady=5, fill="x")

        def display_words():
            for widget in words_frame.winfo_children():
                widget.destroy()
            if not self.current_user.dictionary:
                label = customtkinter.CTkLabel(words_frame, text="Библиотека слов пуста", font=("Arial", 14))
                label.pack(pady=10)
            else:
                for idx, (word, info) in enumerate(self.current_user.dictionary.items(), start=1):
                    word_button = customtkinter.CTkButton(words_frame, text=f"{idx}. {word}", command=lambda w=word: self.show_word_info(w))
                    word_button.pack(pady=5, fill="x")

        display_words()
        back_button = customtkinter.CTkButton(progress_window, text="Назад", command=progress_window.destroy)
        back_button.pack(pady=10)

    def show_word_info(self, word):
        word_info_window = customtkinter.CTkToplevel(self)
        word_info_window.title(f"Информация о слове: {word}")
        word_info_window.geometry("500x00")
        word_info = self.current_user.get_word_info(word)
        definition = word_info["definition"]
        example = word_info["example"]
        transcription = word_info["transcription"]
        translation = word_info["translation"]

        label = customtkinter.CTkLabel(word_info_window, text=f"Слово: {word}", font=("Arial", 20))
        label.pack(pady=10)

        if example == "Слово не найдено":
            error_label = customtkinter.CTkLabel(word_info_window, text="Слово не найдено в словаре.", font=("Arial", 14), text_color="red")
            error_label.pack(pady=5)
        else:
            # definition_label = customtkinter.CTkLabel(word_info_window, text=textwrap.fill(f"Определение: {definition}", width=50), font=("Arial", 14))
            # definition_label.pack(pady=5)

            transcription_label = customtkinter.CTkLabel(word_info_window, text=f"Транскрипция: {transcription}", font=("Arial", 14))
            transcription_label.pack(pady=5)

            translation_label = customtkinter.CTkLabel(word_info_window, text=textwrap.fill(f"Перевод: {translation}", width=50), font=("Arial", 14))
            translation_label.pack(pady=5)

            example_label = customtkinter.CTkLabel(word_info_window, text=textwrap.fill(f"Пример: {example}", width=50), font=("Arial", 14))
            example_label.pack(pady=5)

        back_button = customtkinter.CTkButton(word_info_window, text="Назад", command=word_info_window.destroy)
        back_button.pack(pady=10)

    def show_progress_chart(self):
        progress_window = customtkinter.CTkToplevel(self)
        progress_window.title("Диаграмма прогресса")
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
        back_button = customtkinter.CTkButton(progress_window, text="Назад", command=progress_window.destroy)
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
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("green")
    app = App()
    app.mainloop()