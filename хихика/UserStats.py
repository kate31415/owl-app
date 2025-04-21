import os
import json
import datetime




class UserStats:
    def __init__(self, data_file="user_stats.json"):
        self.data_file = data_file
        self.stats = {}
        self.load_data()
        self.user_data = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.stats = json.load(file)

    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.stats, file, indent=4)

    def update_study_time(self, username, study_duration):
        if username not in self.stats:
            self.stats[username] = {
                "total_study_time": 0,
                "streak_days": 0,
                "last_study_date": None,
                "rewards": [],
                "words": []  # Добавляем поле для слов
            }
        self.stats[username]["total_study_time"] += study_duration
        today = datetime.date.today().isoformat()
        if self.stats[username]["last_study_date"] != today:
            self.stats[username]["streak_days"] += 1
            self.stats[username]["last_study_date"] = today
            self.check_rewards(username)
        self.save_data()

    def check_rewards(self, username):
        streak_days = self.stats[username]["streak_days"]
        rewards = self.stats[username]["rewards"]

        # Пример системы поощрений
        if streak_days % 7 == 0 and streak_days // 7 not in rewards:
            rewards.append(streak_days // 7)
            self.save_data()
            return f"Поздравляем! Вы получили награду за 7-дневный страйк!"
        return None

    def get_user_stats(self, username):
        stats = self.user_data.get(username, {
            "total_study_time": 0,
            "streak_days": 0,
            "last_study_date": None,
            "rewards": [],
            "words": []  # Список слов по умолчанию
        })
        if 'words' not in stats:
            stats['words'] = list(self.get_user(username).dictionary.keys())
        return stats
    

    def get_user(self, username):
        # Возвращаем пользователя по имени (вам нужно будет интегрировать это с вашим классом User)
        # Этот метод возвращает объект пользователя, с которым можно работать
        return self.users[username]  # Пример

    def add_word(self, username, word):
        if username not in self.stats:
            self.stats[username] = {
                "total_study_time": 0,
                "streak_days": 0,
                "last_study_date": None,
                "rewards": [],
                "words": []  # Добавляем поле для слов
            }
        if word not in self.stats[username]["words"]:
            self.stats[username]["words"].append(word)
            self.save_data()
            return f"Слово '{word}' добавлено."
        else:
            return f"Слово '{word}' уже существует."

    def get_words(self, username):
        return self.stats.get(username, {}).get("words", [])