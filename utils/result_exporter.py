def export_to_txt(results_dict, filename="benchmark_results.txt"):
    """
    results_dict: словарь с результатами, например:
        {
          "CPU Integer": 1.234,
          "CPU Float": 2.345,
          "RAM": 0.654,
          "Disk Write": 5.678,
          "Disk Read": 3.210
        }
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for test_name, result in results_dict.items():
                f.write(f"{test_name}: {result:.4f} сек.\n")
    except Exception as e:
        print(f"Ошибка записи в txt-файл: {e}")

def export_to_csv(results_dict, filename="benchmark_results.csv"):
    """
    Аналогичная функция экспорта в CSV
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Заголовок
            f.write("Test,Time (sec)\n")
            for test_name, result in results_dict.items():
                f.write(f"{test_name},{result:.4f}\n")
    except Exception as e:
        print(f"Ошибка записи в csv-файл: {e}")
