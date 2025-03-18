import os
import webbrowser
import requests
from bs4 import BeautifulSoup


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