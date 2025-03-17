import os
import webbrowser
import requests  
from bs4 import BeautifulSoup  
import customtkinter
import csv  

class Dict:
    def __init__(self):
        self.base_url = "https://dictionary.cambridge.org/ru/"

    def fetch_word_info(self, word):
        """Парсинг информации о слове с сайта Cambridge Dictionary."""
        url = f"{self.base_url}dictionary/english/{word}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # определение
            definition_tag = soup.find("div", class_="def ddef_d db")
            definition = definition_tag.text.strip() if definition_tag else "Определение не найдено"

            # пример
            example_tag = soup.find("span", class_="eg deg")
            example = example_tag.text.strip() if example_tag else "Пример не найден"

            # транскрипция
            transcription_tag = soup.find("span", class_="ipa dipa lpr-2 lpl-1")
            transcription = transcription_tag.text.strip() if transcription_tag else "Транскрипция не найдена"

            # перевод
            translation_tag = soup.find("span", class_="trans dtrans")
            translation = translation_tag.text.strip() if translation_tag else "Перевод не найден"

            # Сохранение HTML-страницы для локального просмотра
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
    def __init__(self, app_instance=None):

        #param app_instance: Экземпляр класса App для доступа к методам show_message и clear_window.

        self.app = app_instance
        self.eng_dict = Dict()

    def view_word_page(self, word):

        try:
            html_file = f"{word}_page.html"
            if os.path.exists(html_file):
                webbrowser.open(html_file)
            else:
                self.show_message("Страница слова не найдена.")
        except Exception as e:
            self.show_message(f"Ошибка при открытии страницы: {e}")

    def add_word_from_dict(self):

        self.clear_window()

        label = customtkinter.CTkLabel(self.app, text="Добавить слово из словаря", font=("Arial", 20))
        label.pack(pady=10)

        word_entry = customtkinter.CTkEntry(self.app, placeholder_text="Введите слово")
        word_entry.pack(pady=5)

        def handle_add_word():
            word = word_entry.get().strip().lower()
            if word:
                word_info = self.eng_dict.fetch_word_info(word)
                definition = word_info["definition"]
                example = word_info["example"]
                transcription = word_info["transcription"]
                translation = word_info["translation"]

                # current_user и tracker определены в App
                self.app.current_user.add_word(word, definition, example)
                self.app.tracker.save_data()

                self.show_message(
                    f"Слово '{word}' добавлено!\n"
                    f"Определение: {definition}\n"
                    f"Транскрипция: {transcription}\n"
                    f"Перевод: {translation}\n"
                    f"Пример: {example}"
                )
                self.app.user_menu()

        add_button = customtkinter.CTkButton(self.app, text="Добавить", command=handle_add_word)
        add_button.pack(pady=10)

        back_button = customtkinter.CTkButton(self.app, text="Назад", command=self.app.user_menu)
        back_button.pack(pady=10)

    def show_message(self, message):

        if self.app:
            self.app.show_message(message)

    def clear_window(self):

        if self.app:
            self.app.clear_window()