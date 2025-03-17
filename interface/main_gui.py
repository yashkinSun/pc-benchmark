# file: interface/main_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, Toplevel
from tkinter import ttk
import time

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os

# Импортируем нужные функции из нашего проекта
from utils.ctypes_bridge import (
    cpu_integer_test,  # из C-кода
    cpu_float_test,
    ram_test,
    disk_write_test,
    disk_read_test
)
from utils.result_exporter import export_to_txt, export_to_csv
from utils.system_info import get_system_info  # новый модуль с инфо о ПК

class BenchmarkGUI(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Мини-Бенчмарк производительности ПК")
        self.geometry("800x600")

        # Фоновая картинка
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.set_background(os.path.join(os.path.dirname(__file__), "assets", "default_bg.png"))

        self.results = {}

        # Кнопки управления
        self.btn_run_all = tk.Button(self, text="Запустить все тесты (30s)", command=self.run_all_tests_30s)
        self.btn_run_all.pack(pady=5)

        self.btn_cpu_int = tk.Button(self, text="CPU Integer Test (30s)", command=self.run_cpu_test_30s)
        self.btn_cpu_int.pack(pady=5)

        self.btn_ram = tk.Button(self, text="RAM Test (30s)", command=self.run_ram_test_30s)
        self.btn_ram.pack(pady=5)

        self.btn_disk = tk.Button(self, text="Disk Test (30s)", command=self.run_disk_test_30s)
        self.btn_disk.pack(pady=5)

        self.btn_export_txt = tk.Button(self, text="Экспорт в TXT", command=self.export_results_txt)
        self.btn_export_txt.pack(pady=5)

        self.btn_export_csv = tk.Button(self, text="Экспорт в CSV", command=self.export_results_csv)
        self.btn_export_csv.pack(pady=5)

        self.btn_change_bg = tk.Button(self, text="Сменить фон", command=self.change_bg)
        self.btn_change_bg.pack(pady=5)

        self.btn_show_plot = tk.Button(self, text="Показать график", command=self.show_plot)
        self.btn_show_plot.pack(pady=5)

        # Новая кнопка "О моем ПК"
        self.btn_sys_info = tk.Button(self, text="О моем ПК", command=self.show_system_info)
        self.btn_sys_info.pack(pady=5)

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

    # ----------------------------------------
    # Тесты по 30 секунд
    # ----------------------------------------
    def run_cpu_test_30s(self):
        """
        Запускает целочисленный CPU-бенчмарк на 30 секунд
        с отображением прогресс-бара и модели CPU в окне.
        """
        # Создаём окно-прогресса
        progress_window = Toplevel(self)
        progress_window.title("CPU Test - 30 секунд")
        progress_label = tk.Label(progress_window, text="CPU (Integer ops) Тест выполняется...")
        progress_label.pack(pady=5)

        # Информация о CPU
        cpu_info = get_system_info().get("CPU", "Unknown CPU")
        hw_label = tk.Label(progress_window, text=f"Модель CPU: {cpu_info}")
        hw_label.pack()

        # Прогресс-бар
        progress_bar = ttk.Progressbar(progress_window, length=400, mode='determinate')
        progress_bar['maximum'] = 100
        progress_bar.pack(pady=10)

        # Параметры теста
        CHUNK_ITERATIONS = 10_000_000  # небольшой кусок (10M) для одной итерации
        NUM_THREADS = 4
        total_ops = 0
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            # Запуск порции вычислений
            t0 = time.time()
            cpu_integer_test(CHUNK_ITERATIONS, NUM_THREADS)
            t1 = time.time()

            # Оцениваем, сколько (условных) "итераций" прошло
            # Тут CHUNK_ITERATIONS * num_threads — это грубая метрика, 
            # на самом деле потоков 4, но обычно считаем суммарно.
            total_ops += CHUNK_ITERATIONS * NUM_THREADS

            # Обновляем прогресс-бар (по доле времени)
            elapsed = time.time() - start_time
            progress_bar['value'] = (elapsed / 30) * 100
            progress_window.update()  # перерисовать окно

            # Можно прервать цикл, если время уже перевалило за 30
            if elapsed >= 30:
                break

        total_time = time.time() - start_time
        # "Средний" результат: ops / seconds
        ops_per_sec = total_ops / total_time
        self.results["CPU Integer"] = ops_per_sec

        progress_window.destroy()
        messagebox.showinfo("CPU 30s Test", f"CPU Integer Test завершён.\nСредняя производительность: ~{ops_per_sec:,.0f} ops/sec")

    def run_ram_test_30s(self):
        """
        Аналогичная логика на 30 секунд для RAM:
        циклические вызовы ram_test(...) небольшими блоками,
        пока не пройдет 30 секунд. Считаем MB/s или что-то подобное.
        """
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

            t0 = time.time()
            ram_test(CHUNK_SIZE, ITER_PER_CHUNK)
            t1 = time.time()

            # Объём записанной/прочитанной памяти за эту порцию = CHUNK_SIZE * 2 (запись + чтение).
            # Но для простоты можно считать CHUNK_SIZE, если хочется.
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
        """
        Цикл аналогичен: делаем запись+чтение небольшого файла 
        многократно, пока не пройдёт 30 секунд, 
        в конце выводим усреднённую пропускную способность.
        """
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

        CHUNK_DISK_SIZE = 50 * 1024 * 1024  # 50MB
        total_bytes = 0
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            # Запись
            write_time = disk_write_test("test_file.bin", CHUNK_DISK_SIZE)
            # Чтение
            read_time = disk_read_test("test_file.bin", CHUNK_DISK_SIZE)

            # Считаем общий объём
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

    # ----------------------------------------
    # Запуск "всех тестов" с тремя полосками
    # ----------------------------------------
    def run_all_tests_30s(self):
        """
        Запускаем CPU, RAM, Disk последовательно. 
        Для наглядности делаем три прогресс-бара в одном окне.
        (Если хотите параллельно, придётся усложнить логику и использовать threading в Python.)
        """
        # Окно с тремя прогресс-барами
        all_tests_window = Toplevel(self)
        all_tests_window.title("Запуск всех тестов - 30 секунд каждый")

        label_title = tk.Label(all_tests_window, text="Выполнение 3 тестов подряд (CPU, RAM, Disk), по 30 секунд каждый.")
        label_title.pack(pady=5)

        # Три "под-окна" или три блока
        # Но здесь для упрощения просто три строчки текста + три прогресс-бара
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

        # В реальности мы можем захотеть запускать тесты не "в цикле" в этом же методе,
        # а вынести в отдельные функции. Но здесь для упрощения покажем по аналогии.
        
        # 1) CPU
        self.run_30s_test_with_progressbar(
            test_type="CPU Integer",
            chunk_func=lambda: cpu_integer_test(10_000_000, 4),
            chunk_metric=10_000_000 * 4, 
            bar=cpu_bar,
            parent_window=all_tests_window
        )

        # 2) RAM
        self.run_30s_test_with_progressbar(
            test_type="RAM",
            chunk_func=lambda: ram_test(10 * 1024 * 1024, 1),
            chunk_metric=10 * 1024 * 1024 * 2,  # (10MB * 2) запись+чтение
            bar=ram_bar,
            parent_window=all_tests_window
        )

        # 3) Disk
        self.run_30s_test_with_progressbar(
            test_type="Disk",
            chunk_func=lambda: (disk_write_test("test_file.bin", 50 * 1024 * 1024),
                                disk_read_test("test_file.bin", 50 * 1024 * 1024)),
            chunk_metric=50 * 1024 * 1024 * 2,
            bar=disk_bar,
            parent_window=all_tests_window
        )

        messagebox.showinfo("Все тесты завершены", 
                            f"CPU ops/sec: {self.results.get('CPU Integer',0):,.0f}\n"
                            f"RAM MB/s: {self.results.get('RAM',0):.2f}\n"
                            f"Disk MB/s: {self.results.get('Disk',0):.2f}")
        all_tests_window.destroy()

    def run_30s_test_with_progressbar(self, test_type, chunk_func, chunk_metric, bar, parent_window):
        """
        Универсальный метод для "порционного" 30-секундного теста.
        - test_type: строка для идентификации ("CPU Integer", "RAM", "Disk")
        - chunk_func: функция, вызываемая в цикле (может возвращать None или кортеж, если нужно)
        - chunk_metric: сколько "полезной работы" делается за один вызов chunk_func (в байтах или операциях)
        - bar: прогресс-бар ttk.Progressbar, в который обновлять состояние
        - parent_window: окно, для вызова update()

        По итогу сохраняем результат в self.results[test_type].
        """
        total_work = 0.0
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed >= 30:
                break

            # Выполняем порцию
            chunk_func()
            total_work += chunk_metric

            elapsed = time.time() - start_time
            bar['value'] = (elapsed / 30) * 100
            parent_window.update()

            if elapsed >= 30:
                break

        total_time = time.time() - start_time
        # В зависимости от типа теста, считаем результат:
        if test_type == "CPU Integer":
            # total_work ~ общее число "операций", значит ops/sec:
            value = total_work / total_time
            self.results[test_type] = value
        elif test_type == "RAM":
            # total_work ~ байты, значит MB/s
            value = (total_work / 1024 / 1024) / total_time
            self.results[test_type] = value
        elif test_type == "Disk":
            # тоже MB/s
            value = (total_work / 1024 / 1024) / total_time
            self.results[test_type] = value

    # ----------------------------------------
    # Остальные методы (экспорт, графики, смена фона и т. д.)
    # ----------------------------------------
    def export_results_txt(self):
        export_to_txt(self.results, filename="benchmark_results.txt")
        messagebox.showinfo("Экспорт TXT", "Результаты успешно сохранены в benchmark_results.txt")

    def export_results_csv(self):
        export_to_csv(self.results, filename="benchmark_results.csv")
        messagebox.showinfo("Экспорт CSV", "Результаты успешно сохранены в benchmark_results.csv")

    def change_bg(self):
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
        """
        Открываем новое окно со сводной информацией о ПК.
        """
        info_window = Toplevel(self)
        info_window.title("О моем ПК")

        sys_info = get_system_info()
        info_text = ""
        for key, val in sys_info.items():
            info_text += f"{key}: {val}\n"

        label_info = tk.Label(info_window, text=info_text, justify="left")
        label_info.pack(padx=20, pady=20)

        ok_button = tk.Button(info_window, text="OK", command=info_window.destroy)
        ok_button.pack(pady=5)
