import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import matplotlib
matplotlib.use("TkAgg")  # Используем бэкенд TkAgg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os

from utils.ctypes_bridge import (
    cpu_integer_test, cpu_float_test,
    ram_test, disk_write_test, disk_read_test
)
from utils.result_exporter import export_to_txt, export_to_csv

class BenchmarkGUI(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Мини-Бенчмарк производительности ПК")
        self.geometry("800x600")

        # Путь к фоновому изображению
        self.bg_image_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "default_bg.png"
        )

        # Холст для фонового изображения
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.set_background(self.bg_image_path)

        # Результаты тестов храним в словаре
        self.results = {}

        # Кнопки управления
        self.btn_run_all = tk.Button(self, text="Запустить все тесты", command=self.run_all_tests)
        self.btn_run_all.pack(pady=5)

        self.btn_cpu_int = tk.Button(self, text="CPU Integer Test", command=self.run_cpu_int_test)
        self.btn_cpu_int.pack(pady=5)

        self.btn_cpu_float = tk.Button(self, text="CPU Float Test", command=self.run_cpu_float_test)
        self.btn_cpu_float.pack(pady=5)

        self.btn_ram = tk.Button(self, text="RAM Test", command=self.run_ram_benchmark)
        self.btn_ram.pack(pady=5)

        self.btn_disk = tk.Button(self, text="Disk Tests", command=self.run_disk_tests)
        self.btn_disk.pack(pady=5)

        self.btn_export_txt = tk.Button(self, text="Экспорт в TXT", command=self.export_results_txt)
        self.btn_export_txt.pack(pady=5)

        self.btn_export_csv = tk.Button(self, text="Экспорт в CSV", command=self.export_results_csv)
        self.btn_export_csv.pack(pady=5)

        self.btn_change_bg = tk.Button(self, text="Сменить фон", command=self.change_bg)
        self.btn_change_bg.pack(pady=5)

        self.btn_show_plot = tk.Button(self, text="Показать график", command=self.show_plot)
        self.btn_show_plot.pack(pady=5)

    def set_background(self, image_path):
        """
        Устанавливает фоновое изображение
        """
        if os.path.exists(image_path):
            self.bg_img = tk.PhotoImage(file=image_path)
            self.bg_label.configure(image=self.bg_img)
            self.bg_label.image = self.bg_img
        else:
            self.bg_label.configure(background="gray")

    def run_all_tests(self):
        """
        Запускает все тесты последовательно.
        """
        self.run_cpu_int_test()
        self.run_cpu_float_test()
        self.run_ram_benchmark()
        self.run_disk_tests()
        messagebox.showinfo("Готово", "Все тесты выполнены!")

    def run_cpu_int_test(self):
        # Примерные параметры
        time_taken = cpu_integer_test(10000000, 4)  # 10M итераций, 4 потока
        self.results["CPU Integer"] = time_taken
        messagebox.showinfo("CPU Integer", f"Результат: {time_taken:.4f} сек.")

    def run_cpu_float_test(self):
        time_taken = cpu_float_test(10000000, 4)
        self.results["CPU Float"] = time_taken
        messagebox.showinfo("CPU Float", f"Результат: {time_taken:.4f} сек.")

    def run_ram_benchmark(self):
        # 10МБ для примера, 3 итерации
        time_taken = ram_test(10 * 1024 * 1024, 3)
        self.results["RAM"] = time_taken
        messagebox.showinfo("RAM Benchmark", f"Результат: {time_taken:.4f} сек.")

    def run_disk_tests(self):
        # Запись файла размером 100 МБ
        write_time = disk_write_test("test_file.bin", 100 * 1024 * 1024)
        self.results["Disk Write"] = write_time
        # Чтение того же файла
        read_time = disk_read_test("test_file.bin", 100 * 1024 * 1024)
        self.results["Disk Read"] = read_time
        messagebox.showinfo("Disk Test", f"Запись: {write_time:.4f} сек.\nЧтение: {read_time:.4f} сек.")

    def export_results_txt(self):
        export_to_txt(self.results, filename="benchmark_results.txt")
        messagebox.showinfo("Экспорт TXT", "Результаты успешно сохранены в benchmark_results.txt")

    def export_results_csv(self):
        export_to_csv(self.results, filename="benchmark_results.csv")
        messagebox.showinfo("Экспорт CSV", "Результаты успешно сохранены в benchmark_results.csv")

    def change_bg(self):
        """
        Выбор пользовательского изображения для фона
        """
        file_path = filedialog.askopenfilename(
            title="Выберите изображение для фона",
            filetypes=[("Изображения PNG", "*.png"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.set_background(file_path)

    def show_plot(self):
        """
        Показываем простой столбчатый график результатов.
        """
        if not self.results:
            messagebox.showinfo("Нет данных", "Сначала запустите тесты.")
            return

        fig, ax = plt.subplots(figsize=(6,4))
        test_names = list(self.results.keys())
        test_values = list(self.results.values())

        ax.bar(test_names, test_values, color='skyblue')
        ax.set_ylabel("Время (сек.)")
        ax.set_title("Результаты бенчмарка")

        # Создаём новое окно Tkinter для отображения графика
        plot_window = tk.Toplevel(self)
        plot_window.title("График результатов")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        plt.close(fig)  # Закрываем график в matplotlib, т.к. он уже отрисован в Tk
