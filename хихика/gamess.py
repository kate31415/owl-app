
import customtkinter as ctk
import random
from tkinter import messagebox

class GamesPanel(ctk.CTkToplevel):
    def __init__(self, master, user, learning):
        super().__init__(master)
        self.title("Игры для изучения слов")
        self.geometry("600x500")
        self.user = user
        self.learning = learning
        self.words_list = list(self.user.dictionary.items())

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_flashcards_tab()
        self.create_quiz_tab()
        self.create_match_tab()

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
            self.flash_word_label.configure(text="Нет слов в словаре пользователя.")
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
            self.quiz_result_label.configure(text=f"❌ Неверно! Правильный ответ: {self.quiz_correct}")
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
