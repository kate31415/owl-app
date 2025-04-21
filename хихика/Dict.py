import json
import os
import random
import webbrowser  
import requests  
from bs4 import BeautifulSoup  

class Dict:
    def __init__(self):
        self.base_url = "https://wooordhunt.ru/word/"

    def fetch_word_info(self, word):
        url = f"{self.base_url}{word}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            example_tags = soup.find_all("div", class_="block phrases")
            examples = [tag.text.strip() for tag in example_tags]
            example = "\n".join(examples) if examples else "Пример не найден"

            transcription_tag = soup.find("span", class_="transcription")
            transcription = transcription_tag.text.strip() if transcription_tag else "Транскрипция не найдена"

            translation_tags = soup.find_all("div", class_="t_inline_en")
            translations = [tag.text.strip() for tag in translation_tags]
            translation = "\n".join(translations) if translations else "Перевод не найден"

            with open(f"{word}_page.html", "w", encoding="utf-8") as file:
                file.write(response.text)
               

            return {
                "example": example,
                "transcription": transcription,
                "translation": translation,
            }
        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return {
                "example": "Ошибка",
                "transcription": "",
                "translation": "",
            }

class Learning:
    def __init__(self):
        self.dict = Dict()
        self.user_words = {}  # Словарь изученных слов
        self.themes = self.load_themes_from_json()
        self.points = 0  # Очки игрока
        self.level = 1   # Начальный уровень
        self.user_words = {}

    def load_themes_from_json(self):
        file_path = os.path.join(os.path.dirname(__file__), "themes.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Ошибка в формате JSON: {e}")
                return {}
        else:
            print("Файл themes.json не найден!")
            return {}

    def get_words_by_theme(self, theme_name):
        return self.themes.get(theme_name.lower(), {})

    def add_word(self, word):
        word_info = self.dict.fetch_word_info(word)
        self.user_words[word] = word_info
        return word_info

    def add_word_from_dict(self, word):  
        word_info = self.dict.fetch_word_info(word)  
        example = word_info["example"]  
        transcription = word_info["transcription"]  
        translation = word_info["translation"] 

    def get_progress_data(self):
        # Прогресс по словам, а не по темам
        word_count = len(self.user_words)
        return {"Изученные слова": word_count}

    def get_random_word(self, theme_name):
        words = self.get_words_by_theme(theme_name)
        if words:
            return random.choice(list(words.keys())), words
        return None, None
    

