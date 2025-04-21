import json
import os

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

            # Парсим примеры использования  
            example_tags = soup.find_all("div", class_="block phrases")  
            examples = [tag.text.strip() for tag in example_tags]  
            example = "\n".join(examples) if examples else "Пример не найден"  

            # Парсим транскрипцию  
            transcription_tag = soup.find("span", class_="transcription")  
            transcription = transcription_tag.text.strip() if transcription_tag else "Транскрипция не найдена"  

            # Парсим перевод  
            translation_tags = soup.find_all("div", class_="t_inline_en")  
            translations = [tag.text.strip() for tag in translation_tags]  
            translation = "\n".join(translations) if translations else "Перевод не найден"  

            # Сохраняем страницу в HTML  
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

    def load_themes_from_json(self):
        file_path = os.path.join(os.path.dirname(__file__), "themes.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            raise FileNotFoundError("Файл themes.json не найден!")

    def get_words_by_theme(self, theme_name):
        return self.themes.get(theme_name.lower(), {})

    def add_word_to_user_dict(self, user, word, translation):
        user.add_word(
            word,
            definition="",
            example=f"Пример использования: {word} - это {translation}.",
            transcription="Транскрипция отсутствует",
            translation=translation
        )

    def load_themes_from_json(self):
        file_path = os.path.join(os.path.dirname(__file__), "themes.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        else:
            raise FileNotFoundError("Файл themes.json не найден!")

    def get_words_by_theme(self, theme_name):
        return self.themes.get(theme_name.lower(), {})

    def add_word_to_user_dict(self, user, word, translation):
        user.add_word(
            word,
            definition="",
            example=f"Пример использования: {word} - это {translation}.",
            transcription="Транскрипция отсутствует",
            translation=translation
        )

    # def view_word_page(self, word):  
    #     try:  
    #         html_file = f"{word}_page.html"  
    #         if os.path.exists(html_file):  
    #             webbrowser.open(html_file)  
    #         else:  
    #             print("Страница слова не найдена.")  
    #     except Exception as e:  
    #         print(f"Ошибка при открытии страницы: {e}")  

    # def add_word_from_dict(self, word):
    #     word_info = self.dict.fetch_word_info(word)
    #     if word_info is None:
    #         return {
    #             "example": "Слово не найдено",
    #             "transcription": "Транскрипция не найдена",
    #             "translation": "Перевод не найден"
    #         }
    #     return word_info

    def add_word_from_dict(self, word):  
        word_info = self.dict.fetch_word_info(word)  
        example = word_info["example"]  
        transcription = word_info["transcription"]  
        translation = word_info["translation"]  
        
    #     print(  
    #         f"Слово '{word}' добавлено!\n"  
    #         f"Транскрипция: {transcription}\n"  
    #         f"Перевод: {translation}\n"  
    #         f"Пример: {example}"  
    #     )  


# # Основная функция для проверки работы кода  
# def main():  
#     learning = Learning()  
#     word = input("Введите слово для парсинга: ")  
#     learning.add_word_from_dict(word)  
#     learning.view_word_page(word)  

# if __name__ == "__main__":  
#     main()  

        # word_info = self.dict.fetch_word_info(word)  
        # example = textwrap.wrap(word_info["example"], 50)  
        # transcription = word_info["transcription"]  
        # translation = textwrap.wrap(word_info["translation"], 50)
        # # description_lines = textwrap.wrap(book['description'], 50)