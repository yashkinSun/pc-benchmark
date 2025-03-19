import tkinter as tk
import os

# Импортируем фрейм с кнопками
from interface.benchmark_buttons import BenchmarkButtonsFrame

class MainGUI(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Мини-Бенчмарк ПК – Улучшенная версия")
        self.geometry("800x600")

        # Устанавливаем фоновую картинку (по аналогии со старым кодом)
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        default_bg_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "default_bg.png"
        )
        self.set_background(default_bg_path)

        # Разделяем окно: верхние 40% и нижние 60%
        self.top_frame = tk.Frame(self, height=int(0.4 * 600), bg="lightgray")
        self.top_frame.pack(fill=tk.X, side=tk.TOP)

        self.bottom_frame = tk.Frame(self, height=int(0.6 * 600))
        self.bottom_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

        # Вверху можно разместить какую-либо надпись или лого
        title_label = tk.Label(self.top_frame, text="Добро пожаловать в наш бенчмарк!", bg="lightgray")
        title_label.pack(pady=20)

        # Во "фрейме кнопок" и будет 2-колоночное расположение кнопок
        self.buttons_frame = BenchmarkButtonsFrame(self.bottom_frame)
        self.buttons_frame.pack(expand=True, fill=tk.BOTH)

    def set_background(self, image_path):
        """
        Устанавливает фоновое изображение для всего окна
        """
        if os.path.exists(image_path):
            self.bg_img = tk.PhotoImage(file=image_path)
            self.bg_label.configure(image=self.bg_img)
            self.bg_label.image = self.bg_img
        else:
            self.bg_label.configure(background="gray")
