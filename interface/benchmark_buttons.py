import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from tkinter import ttk
import time
import os

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.ctypes_bridge import (
    cpu_integer_test,
    cpu_float_test,
    ram_test,
    disk_write_test,
    disk_read_test
)
from utils.result_exporter import export_to_txt, export_to_csv
from utils.system_info import get_system_info


class BenchmarkButtonsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.results = {}

        # Левый фрейм (колонка 1)
        self.left_col = tk.Frame(self)
        self.left_col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Правый фрейм (колонка 2)
        self.right_col = tk.Frame(self)
        self.right_col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Итого 10 кнопок, 5 в каждой колонке
        # --------------------------------------------
        # Левая колонка:
        self.btn_run_all = tk.Button(self.left_col, text="Запустить все тесты (30s)", command=self.run_all_tests_30s)
        self.btn_run_all.pack(pady=5, fill=tk.X)

        self.btn_cpu_int = tk.Button(self.left_col, text="CPU Integer Test (30s)", command=self.run_cpu_test_30s)
        self.btn_cpu_int.pack(pady=5, fill=tk.X)

        self.btn_ram = tk.Button(self.left_col, text="RAM Test (30s)", command=self.run_ram_test_30s)
        self.btn_ram.pack(pady=5, fill=tk.X)

        self.btn_disk = tk.Button(self.left_col, text="Disk Test (30s)", command=self.run_disk_test_30s)
        self.btn_disk.pack(pady=5, fill=tk.X)

        self.btn_show_plot = tk.Button(self.left_col, text="Показать график", command=self.show_plot)
        self.btn_show_plot.pack(pady=5, fill=tk.X)

        # --------------------------------------------
        # Правая колонка:
        self.btn_export_txt = tk.Button(self.right_col, text="Экспорт в TXT", command=self.export_results_txt)
        self.btn_export_txt.pack(pady=5, fill=tk.X)

        self.btn_export_csv = tk.Button(self.right_col, text="Экспорт в CSV", command=self.export_results_csv)
        self.btn_export_csv.pack(pady=5, fill=tk.X)

        self.btn_change_bg = tk.Button(self.right_col, text="Сменить фон", command=self.change_bg)
        self.btn_change_bg.pack(pady=5, fill=tk.X)

        self.btn_sys_info = tk.Button(self.right_col, text="О моём ПК", command=self.show_system_info)
        self.btn_sys_info.pack(pady=5, fill=tk.X)

        self.btn_about = tk.Button(self.right_col, text="Об авторах", command=self.show_authors)
        self.btn_about.pack(side=tk.BOTTOM, pady=20, fill=tk.X)

    # ---------------------------------------------------------
    # 30-секундные тесты (CPU, RAM, Disk) — логика из старого main_gui
    # ---------------------------------------------------------
    def run_cpu_test_30s(self):
        progress_window = Toplevel(self)
        progress_window.title("CPU Test - 30 секунд")
        progress_label = tk.Label(progress_window, text="CPU (Integer ops) Тест выполняется...")
        progress_label.pack(pady=5)

        cpu_info = get_system_info().get("CPU", "Unknown CPU")
        hw_label = tk.Label(progress_window, text=f"Модель CPU: {cpu_info}")
        hw_label.pack()

        progress_bar = ttk.Progressbar(progress_window, length=400, mode='determinate')
        progress_bar['maximum'] = 100
        progress_bar.pack(pady=10)

        CHUNK_ITERATIONS = 10_000_000
        NUM_THREADS = 4
        total_ops = 0
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            cpu_integer_test(CHUNK_ITERATIONS, NUM_THREADS)
            total_ops += CHUNK_ITERATIONS * NUM_THREADS

            elapsed = time.time() - start_time
            progress_bar['value'] = (elapsed / 30) * 100
            progress_window.update()

            if elapsed >= 30:
                break

        total_time = time.time() - start_time
        ops_per_sec = total_ops / total_time
        self.results["CPU Integer"] = ops_per_sec

        progress_window.destroy()
        messagebox.showinfo("CPU 30s Test", f"CPU Integer Test завершён.\nСредняя производительность: ~{ops_per_sec:,.0f} ops/sec")

    def run_ram_test_30s(self):
        progress_window = Toplevel(self)
        progress_window.title("RAM Test - 30 секунд")
        progress_label = tk.Label(progress_window, text="RAM Тест выполняется...")
        progress_label.pack(pady=5)

        ram_info = get_system_info().get("RAM", "Unknown RAM")
        hw_label = tk.Label(progress_window, text=f"Модель RAM: {ram_info}")
        hw_label.pack()

        progress_bar = ttk.Progressbar(progress_window, length=400, mode='determinate')
        progress_bar['maximum'] = 100
        progress_bar.pack(pady=10)

        CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB
        ITER_PER_CHUNK = 1
        total_bytes = 0
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            ram_test(CHUNK_SIZE, ITER_PER_CHUNK)
            # Запись + чтение
            total_bytes += CHUNK_SIZE * 2

            elapsed = time.time() - start_time
            progress_bar['value'] = (elapsed / 30) * 100
            progress_window.update()

            if elapsed >= 30:
                break

        total_time = time.time() - start_time
        mb_s = (total_bytes / 1024 / 1024) / total_time
        self.results["RAM"] = mb_s

        progress_window.destroy()
        messagebox.showinfo("RAM 30s Test", f"RAM Test завершён.\nСредняя скорость: ~{mb_s:.2f} MB/s")

    def run_disk_test_30s(self):
        progress_window = Toplevel(self)
        progress_window.title("Disk Test - 30 секунд")
        progress_label = tk.Label(progress_window, text="Disk Тест выполняется...")
        progress_label.pack(pady=5)

        disk_info = get_system_info().get("Disk", "Unknown Disk")
        hw_label = tk.Label(progress_window, text=f"Накопитель: {disk_info}")
        hw_label.pack()

        progress_bar = ttk.Progressbar(progress_window, length=400, mode='determinate')
        progress_bar['maximum'] = 100
        progress_bar.pack(pady=10)

        CHUNK_DISK_SIZE = 50 * 1024 * 1024
        total_bytes = 0
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            write_time = disk_write_test("test_file.bin", CHUNK_DISK_SIZE)
            read_time = disk_read_test("test_file.bin", CHUNK_DISK_SIZE)
            total_bytes += CHUNK_DISK_SIZE * 2

            elapsed = time.time() - start_time
            progress_bar['value'] = (elapsed / 30) * 100
            progress_window.update()

            if elapsed >= 30:
                break

        total_time = time.time() - start_time
        mb_s = (total_bytes / 1024 / 1024) / total_time
        self.results["Disk"] = mb_s

        progress_window.destroy()
        messagebox.showinfo("Disk 30s Test", f"Disk Test завершён.\nСредняя скорость: ~{mb_s:.2f} MB/s")

    # ---------------------------------------------------------
    # Запуск всех тестов (CPU, RAM, Disk) последовательно
    # ---------------------------------------------------------
    def run_all_tests_30s(self):
        all_tests_window = Toplevel(self)
        all_tests_window.title("Запуск всех тестов - 30 секунд каждый")

        label_title = tk.Label(all_tests_window, text="Выполнение 3 тестов подряд (CPU, RAM, Disk), по 30 секунд каждый.")
        label_title.pack(pady=5)

        cpu_label = tk.Label(all_tests_window, text="CPU:")
        cpu_label.pack()
        cpu_bar = ttk.Progressbar(all_tests_window, length=400, mode='determinate', maximum=100)
        cpu_bar.pack(pady=5)

        ram_label = tk.Label(all_tests_window, text="RAM:")
        ram_label.pack()
        ram_bar = ttk.Progressbar(all_tests_window, length=400, mode='determinate', maximum=100)
        ram_bar.pack(pady=5)

        disk_label = tk.Label(all_tests_window, text="Disk:")
        disk_label.pack()
        disk_bar = ttk.Progressbar(all_tests_window, length=400, mode='determinate', maximum=100)
        disk_bar.pack(pady=5)

        # Запускаем 3 теста по очереди (chunk-based), используя универсальную функцию
        self.run_30s_test_with_progressbar(
            test_type="CPU Integer",
            chunk_func=lambda: cpu_integer_test(10_000_000, 4),
            chunk_metric=10_000_000 * 4,
            bar=cpu_bar,
            parent_window=all_tests_window
        )

        self.run_30s_test_with_progressbar(
            test_type="RAM",
            chunk_func=lambda: ram_test(10 * 1024 * 1024, 1),
            chunk_metric=10 * 1024 * 1024 * 2,
            bar=ram_bar,
            parent_window=all_tests_window
        )

        self.run_30s_test_with_progressbar(
            test_type="Disk",
            chunk_func=lambda: (disk_write_test("test_file.bin", 50 * 1024 * 1024),
                                disk_read_test("test_file.bin", 50 * 1024 * 1024)),
            chunk_metric=50 * 1024 * 1024 * 2,
            bar=disk_bar,
            parent_window=all_tests_window
        )

        # Выводим итог
        msg = (
            f"CPU ops/sec: {self.results.get('CPU Integer',0):,.0f}\n"
            f"RAM MB/s: {self.results.get('RAM',0):.2f}\n"
            f"Disk MB/s: {self.results.get('Disk',0):.2f}"
        )
        messagebox.showinfo("Все тесты завершены", msg)
        all_tests_window.destroy()

    def run_30s_test_with_progressbar(self, test_type, chunk_func, chunk_metric, bar, parent_window):
        total_work = 0.0
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            # Выполняем "порцию" вычислений
            chunk_func()
            total_work += chunk_metric

            elapsed = time.time() - start_time
            bar['value'] = (elapsed / 30) * 100
            parent_window.update()

            if elapsed >= 30:
                break

        total_time = time.time() - start_time
        # Считаем конечную метрику
        if test_type == "CPU Integer":
            # total_work ~ кол-во операций, => ops/sec
            value = total_work / total_time
            self.results[test_type] = value
        elif test_type == "RAM":
            # total_work ~ байты => MB/s
            value = (total_work / 1024 / 1024) / total_time
            self.results[test_type] = value
        elif test_type == "Disk":
            # total_work ~ байты => MB/s
            value = (total_work / 1024 / 1024) / total_time
            self.results[test_type] = value

    # ---------------------------------------------------------
    # Экспорт, смена фона, график
    # ---------------------------------------------------------
    def export_results_txt(self):
        export_to_txt(self.results, filename="benchmark_results.txt")
        messagebox.showinfo("Экспорт TXT", "Результаты успешно сохранены в benchmark_results.txt")

    def export_results_csv(self):
        export_to_csv(self.results, filename="benchmark_results.csv")
        messagebox.showinfo("Экспорт CSV", "Результаты успешно сохранены в benchmark_results.csv")

    def change_bg(self):
        """
        Выбор пользовательского фона.
        Чтобы реально сменить фон, нужно доступ к методу set_background
        у родительского окна MainGUI. 
        Для упрощения тут делаем поиск через master... 
        """
        file_path = filedialog.askopenfilename(
            title="Выберите изображение для фона",
            filetypes=[("Изображения PNG", "*.png"), ("Все файлы", "*.*")]
        )
        if file_path:
            # Ищем родителя типа MainGUI, чтобы вызвать set_background
            top = self._root()
            if hasattr(top, 'set_background'):
                top.set_background(file_path)

    def show_plot(self):
        if not self.results:
            messagebox.showinfo("Нет данных", "Сначала запустите тесты.")
            return

        fig, ax = plt.subplots(figsize=(6, 4))
        test_names = list(self.results.keys())
        test_values = list(self.results.values())

        ax.bar(test_names, test_values, color='green')
        ax.set_ylabel("Производительность (зависит от теста)")
        ax.set_title("Результаты бенчмарка")

        plot_window = tk.Toplevel(self)
        plot_window.title("График результатов")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        plt.close(fig)

    def show_system_info(self):
        info_window = Toplevel(self)
        info_window.title("О моём ПК")

        sys_info = get_system_info()
        info_text = ""
        for key, val in sys_info.items():
            info_text += f"{key}: {val}\n"

        label_info = tk.Label(info_window, text=info_text, justify="left")
        label_info.pack(padx=20, pady=20)

        ok_button = tk.Button(info_window, text="OK", command=info_window.destroy)
        ok_button.pack(pady=5)

    def show_authors(self):
        """
        Окошко "Об авторах". Можно сделать отдельный файл, 
        но ради примера оставим тут.
        """
        authors_window = Toplevel(self)
        authors_window.title("Об авторах")
        msg = (
            "Данная программа разработана:\n"
            "- yashkinSun\n"
            "- @alysrazzor\n"
            "- ...\n\n"
            "Все права защищены © 2025"
        )
        label = tk.Label(authors_window, text=msg, justify=tk.LEFT)
        label.pack(padx=20, pady=20)

        close_btn = tk.Button(authors_window, text="Закрыть", command=authors_window.destroy)
        close_btn.pack(pady=10)
