import random
import customtkinter
from tkinter import messagebox
# from main.py import show_word_info()

class WordGuessGame:
    def __init__(self, user):
        self.user = user

    def get_random_words(self, correct_word):
        all_words = list(self.user.dictionary.keys())
        if len(all_words) < 4:
            raise ValueError("Необходимо добавить больше слов для игры.")
        
        # Убедимся, что правильное слово входит в выборку
        selected_words = random.sample([word for word in all_words if word != correct_word], 3)
        selected_words.append(correct_word)
        random.shuffle(selected_words)
        return selected_words

    def play_game(self):
        all_words = list(self.user.dictionary.keys())
        if len(all_words) == 0:
            self.show_message("Ваш словарь пуст. Добавьте слова для игры.")
            return
        
        correct_word = random.choice(all_words)
        word_info = self.user.get_word_info(correct_word)
        definition = word_info["definition"]
        example = word_info["example"]
        transcription = word_info["transcription"]
        translation = word_info["translation"]

        selected_words = self.get_random_words(correct_word)

        game_window = customtkinter.CTkToplevel()
        game_window.title("Угадай слово")
        game_window.geometry("400x400")

        label = customtkinter.CTkLabel(game_window, text=f"Угадай слово по переводу:\n{translation}", font=("Arial", 16))
        label.pack(pady=10)

        def check_answer(selected_word):
            if selected_word == correct_word:
                self.show_message("Правильно!")
            else:
                self.show_message(f"Неправильно! Правильный ответ: {correct_word}")
            game_window.destroy()

        for word in selected_words:
            button = customtkinter.CTkButton(game_window, text=word, command=lambda w=word: check_answer(w))
            button.pack(pady=5, fill="x")

        back_button = customtkinter.CTkButton(game_window, text="Назад", command=game_window.destroy)
        back_button.pack(pady=10)

    def show_message(self, message):
        label = customtkinter.CTkLabel(self, text=message, font=("Arial", 14))
        label.pack(pady=10)