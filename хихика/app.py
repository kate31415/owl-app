import customtkinter as ctk
from Dict import Dict, Learning
from User import User, ProgressTracker
from UserStats import UserStats
from gamesss import GamesPanel

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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.learning = Learning()
        self.title("Английский словарь")
        self.geometry("800x650")

        self.input = ctk.CTkEntry(self, width=300, placeholder_text="Введите слово или перевод")
        self.input.pack(pady=10)

        self.search_btn = ctk.CTkButton(self, text="Поиск", command=self.lookup_word)
        self.search_btn.pack(pady=5)

        self.output = ctk.CTkTextbox(self, width=600, height=200)
        self.output.pack(pady=10)

        self.progress_btn = ctk.CTkButton(self, text="Показать прогресс", command=self.show_progress)
        self.progress_btn.pack(pady=10)

        self.view_words_btn = ctk.CTkButton(self, text="Показать изученные слова", command=self.show_learned_words)
        self.view_words_btn.pack(pady=5)

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

        self.check_btn = ctk.CTkButton(self, text="Проверить ответ", command=self.check_answer)
        self.check_btn.pack(pady=5)

        self.game_output = ctk.CTkTextbox(self, width=600, height=100)
        self.game_output.pack(pady=10)

        self.current_word = None
        self.correct_answer = None

    def show_learned_words(self):
        # Получаем все слова, которые были изучены
        learned_words = self.learning.get_progress_data()

        # Формируем список из всех изученных слов
        learned_words_list = "\n".join([f"{word}: {info['translation']}" for word, info in learned_words.items()])

        # Если слов нет, показываем сообщение
        if not learned_words_list:
            learned_words_list = "Вы еще не изучили ни одного слова."

        # Отображаем их в поле game_output
        self.game_output.delete("1.0", "end")
        self.game_output.insert("1.0", f"Изученные слова:\n{learned_words_list}")

    def lookup_word(self):
        word = self.input.get().strip()
        if word:
            self.learning.add_word(word)
            word_info = self.learning.user_words[word]
            result = f"Слово: {word}\nТранскрипция: {word_info['transcription']}\nПеревод: {word_info['translation']}\nПримеры:\n{word_info['example']}"
            self.output.delete("1.0", "end")
            self.output.insert("1.0", result)

    def show_progress(self):
        progress = self.learning.get_progress_data()

        fig, ax = plt.subplots()
        words = list(progress.keys())
        counts = [1] * len(words)

        ax.bar(words, counts)
        ax.set_title("Прогресс по словам")
        ax.set_ylabel("Изучено (1 = изучено)")
        ax.set_xlabel("Слова")
        plt.xticks(rotation=45, ha="right")

        top = tk.Toplevel(self)
        top.title("Диаграмма прогресса")
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack()

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

    def check_answer(self):
        if not self.current_word or not self.correct_answer:
            return

        user_answer = self.input.get().strip().lower()
        correct_answers = [ans.strip().lower() for ans in self.correct_answer.split(",")]

        self.input.delete(0, "end")

        if user_answer in correct_answers:
            self.learning.update_points(True)  # Обновление очков и уровня
            self.game_output.insert("end", "\n✅ Правильный ответ!")
        else:
            correct_answer_text = ", ".join(correct_answers)
            self.game_output.insert("end", f"\n❌ Неправильно. Правильный ответ: {correct_answer_text}")

        self.after(2000, self.start_game)