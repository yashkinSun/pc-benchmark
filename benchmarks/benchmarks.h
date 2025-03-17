#ifndef BENCHMARKS_H
#define BENCHMARKS_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Функции для CPU-бенчмарка
 * run_cpu_integer_ops:    Выполнение целочисленных операций
 * run_cpu_float_ops:      Выполнение операций с плавающей точкой
 * 
 * Параметры:
 *   iterations   - количество итераций цикла
 *   num_threads  - количество потоков
 * Возвращает время (в секундах), затраченное на тест.
 */
double run_cpu_integer_ops(int iterations, int num_threads);
double run_cpu_float_ops(int iterations, int num_threads);

/*
 * Функция для RAM-бенчмарка
 * run_ram_benchmark: измерение скорости чтения/записи в ОЗУ
 * 
 * Параметры:
 *   data_size_bytes  - объём памяти, с которым работаем
 *   iterations       - число повторных проходов
 * Возвращает время (в секундах), затраченное на тест.
 */
double run_ram_benchmark(long data_size_bytes, int iterations);

/*
 * Функции для DISK-бенчмарка
 * run_disk_write_test: запись тестового файла
 * run_disk_read_test:  чтение тестового файла
 * 
 * Параметры:
 *   filename          - имя тестового файла
 *   file_size_bytes   - размер файла в байтах
 * Возвращает время (в секундах), затраченное на тест.
 */
double run_disk_write_test(const char* filename, long file_size_bytes);
double run_disk_read_test(const char* filename, long file_size_bytes);

#ifdef __cplusplus
}
#endif

#endif
