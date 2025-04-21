import customtkinter as ctk
import random
import tkinter as tk
from tkinter import messagebox
from Dict import Dict, Learning

# ПОЧЕМУ ДОСТУП К ДИКУ НЕ ОСУЩЕСТВЛЯЕТСЯ

class GamesPanel(ctk.CTkToplevel):
    def __init__(self, master, user, learning):
        super().__init__(master)
        self.title("Игры для изучения слов")
        self.geometry("600x500")
        self.user = user
        self.learning = learning
        self.words_list = list(self.user.dictionary.items())  # Слова пользователя
        self.themes_words = {}  # Слова из тем
        self.current_source = "Изученные слова"  # Источник слов по умолчанию
        self.theme_var = tk.StringVar()
        themes_list = list(self.learning.themes.keys()) or ["еда"]  # запасной вариант
        self.theme_var.set(themes_list[0])


        # Фрейм для выбора источника слов
        self.game_source_frame = ctk.CTkFrame(self)
        self.game_source_frame.pack(pady=10)

        self.game_source_var = ctk.StringVar(value="Изученные слова")

        self.radio_button_study = ctk.CTkRadioButton(
            self.game_source_frame,
            text="Изученные слова",
            variable=self.game_source_var,
            value="Изученные слова",
            command=self.update_word_source
        )
        self.radio_button_study.pack(side="left", padx=10)

        self.radio_button_themes = ctk.CTkRadioButton(
            self.game_source_frame,
            text="Темы",
            variable=self.game_source_var,
            value="Темы",
            command=self.update_word_source
        )
        self.radio_button_themes.pack(side="left", padx=10)

        # Вкладки для игр
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_flashcards_tab()
        self.create_quiz_tab()
        self.create_match_tab()

    def get_progress_data(self):
        return self.learning.user_words

    def show_learned_words(self):
        # Получаем все слова, которые были изучены
        learned_words = self.learning.get_progress_data()

        # Формируем список из всех изученных слов
        learned_words_list = "\n".join([f"{word}: {info['translation']}" for word, info in learned_words.items()])

        # Если слов нет, показываем сообщение
        if not learned_words_list:
            learned_words_list = "Вы еще не изучили ни одного слова."

    def update_word_source(self):
        """Обновляет источник слов для игр."""
        source = self.game_source_var.get()
        if source == "Изученные слова":
            self.current_source = "Изученные слова"
            self.words_list = list(self.user.dictionary.items())
        elif source == "Темы":
            self.current_source = "Темы"
            self.load_theme_words()

    def get_words_by_theme(self, theme_name):
        return self.themes.get(theme_name.lower(), {})

    def load_theme_words(self):
        """Загружает слова из тем."""
        theme_name = "default"  # Здесь можно добавить выбор темы через интерфейс
        self.themes_words = self.learning.get_words_by_theme(theme_name)
        self.words_list = list(self.themes_words.items())

    def create_flashcards_tab(self):
        self.flash_tab = self.tabview.add("Флеш-карточки")
        self.flash_word_label = ctk.CTkLabel(self.flash_tab, text="", font=("Arial", 22))
        self.flash_word_label.pack(pady=20)
        self.flash_result_label = ctk.CTkLabel(self.flash_tab, text="", font=("Arial", 18))
        self.flash_result_label.pack(pady=10)
        ctk.CTkButton(self.flash_tab, text="Новое слово", command=self.new_flashcard).pack(pady=5)
        ctk.CTkButton(self.flash_tab, text="Показать перевод", command=self.show_flash_translation).pack(pady=5)
        self.new_flashcard()

    def new_flashcard(self):
        if not self.words_list:
            self.flash_word_label.configure(text="Нет слов для игры.")
            self.flash_result_label.configure(text="")
            return
        self.current_flash = random.choice(self.words_list)
        self.flash_word_label.configure(text=self.current_flash[0])
        self.flash_result_label.configure(text="")

    def show_flash_translation(self):
        self.flash_result_label.configure(text=self.current_flash[1]["translation"])

    def create_quiz_tab(self):
        self.quiz_tab = self.tabview.add("Викторина")
        self.quiz_word_label = ctk.CTkLabel(self.quiz_tab, text="", font=("Arial", 22))
        self.quiz_word_label.pack(pady=20)
        self.quiz_result_label = ctk.CTkLabel(self.quiz_tab, text="", font=("Arial", 16))
        self.quiz_result_label.pack(pady=10)
        self.quiz_buttons_frame = ctk.CTkFrame(self.quiz_tab)
        self.quiz_buttons_frame.pack(pady=5)
        self.load_quiz()

    def load_quiz(self):
        if len(self.words_list) < 4:
            self.quiz_word_label.configure(text="Добавьте больше слов для викторины.")
            return
        for widget in self.quiz_buttons_frame.winfo_children():
            widget.destroy()

        word, correct_info = random.choice(self.words_list)
        correct = correct_info["translation"]
        self.quiz_word_label.configure(text=word)
        self.quiz_correct = correct
        options = [correct] + random.sample(
            [v["translation"] for k, v in self.words_list if v["translation"] != correct], 3)
        random.shuffle(options)

        for option in options:
            btn = ctk.CTkButton(self.quiz_buttons_frame, text=option, command=lambda o=option: self.check_quiz(o))
            btn.pack(pady=2)

    def check_quiz(self, selected):
        if selected == self.quiz_correct:
            self.quiz_result_label.configure(text="✅ Верно!")
        else:
            self.quiz_result_label.configure(text=f"❌ Неверно! Правильный ответ: {self.quiz_correct.strip()}")
        self.after(2000, self.load_quiz)

    def create_match_tab(self):
        self.match_tab = self.tabview.add("Соедини пары")
        self.match_labels = []
        self.match_menus = []
        self.match_result_label = ctk.CTkLabel(self.match_tab, text="", font=("Arial", 16))
        self.match_result_label.pack(pady=5)
        ctk.CTkButton(self.match_tab, text="Новая игра", command=self.load_match_game).pack(pady=5)
        ctk.CTkButton(self.match_tab, text="Проверить", command=self.check_matches).pack(pady=5)
        self.load_match_game()

    def load_match_game(self):
        for label in self.match_labels:
            label.destroy()
        for menu in self.match_menus:
            menu[0].destroy()

        self.match_labels.clear()
        self.match_menus.clear()

        if len(self.words_list) < 4:
            self.match_result_label.configure(text="Добавьте больше слов для игры.")
            return

        self.match_pairs = random.sample(self.words_list, 4)
        translations = [info["translation"] for _, info in self.match_pairs]
        random.shuffle(translations)

        for i, (word, info) in enumerate(self.match_pairs):
            lbl = ctk.CTkLabel(self.match_tab, text=word)
            lbl.pack()
            var = ctk.StringVar(value="Выбери перевод")
            menu = ctk.CTkOptionMenu(self.match_tab, variable=var, values=translations)
            menu.pack()
            self.match_labels.append(lbl)
            self.match_menus.append((menu, info["translation"]))

    def check_matches(self):
        correct = 0
        for menu, expected in self.match_menus:
            if menu.get() == expected:
                correct += 1
        self.match_result_label.configure(text=f"Результат: {correct} из 4")