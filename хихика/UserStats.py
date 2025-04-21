import os
import json
import datetime
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class UserStats:
    def __init__(self, data_file="user_stats.json"):
        self.data_file = data_file
        self.stats = {}
        self.load_data()

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
                "rewards": []
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
        return self.stats.get(username, {
            "total_study_time": 0,
            "streak_days": 0,
            "last_study_date": None,
            "rewards": []
        })

# class UserStatsApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Статистика пользователей")
#         self.user_stats = UserStats()

#         # Создаем интерфейс
#         self.create_widgets()

#     def create_widgets(self):
#         # Поле для ввода имени пользователя
#         tk.Label(self.root, text="Имя пользователя:").grid(row=0, column=0, padx=10, pady=5)
#         self.username_entry = tk.Entry(self.root)
#         self.username_entry.grid(row=0, column=1, padx=10, pady=5)

#         # Кнопка для получения статистики
#         tk.Button(self.root, text="Показать статистику", command=self.show_user_stats).grid(row=0, column=2, padx=10, pady=5)

#         # Таблица для отображения данных
#         columns = ("Параметр", "Значение")
#         self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
#         self.tree.heading("Параметр", text="Параметр")
#         self.tree.heading("Значение", text="Значение")
#         self.tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

#     def show_user_stats(self):
#         # Очистка таблицы перед обновлением
#         for item in self.tree.get_children():
#             self.tree.delete(item)

#         # Получение имени пользователя
#         username = self.username_entry.get()
#         if not username:
#             self.tree.insert("", "end", values=("Ошибка", "Введите имя пользователя"))
#             return

#         # Получение статистики пользователя
#         stats = self.user_stats.get_user_stats(username)

#         # Отображение данных в таблице
#         self.tree.insert("", "end", values=("Общее время обучения (сек)", stats["total_study_time"]))
#         self.tree.insert("", "end", values=("Количество дней подряд", stats["streak_days"]))
#         self.tree.insert("", "end", values=("Последняя дата обучения", stats["last_study_date"]))
#         self.tree.insert("", "end", values=("Награды", ", ".join(map(str, stats["rewards"]))))

# Запуск приложения
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = UserStatsApp(root)
#     root.mainloop()