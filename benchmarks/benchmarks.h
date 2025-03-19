#ifndef BENCHMARKS_H
#define BENCHMARKS_H

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------- CPU Tests ---------------- */

/* Существующие */
double run_cpu_integer_ops(int iterations, int num_threads);
double run_cpu_float_ops(int iterations, int num_threads);

/* Новый: многопоточная CPU-нагрузка (комбинация int и float) */
double run_cpu_multithread_load(int iterations_per_thread, int num_threads);

/* ---------------- RAM Tests ---------------- */

/* Существующая */
double run_ram_benchmark(long data_size_bytes, int iterations);

/* Новая: измерение латентности (простейшая заглушка) */
double run_ram_latency_test(long data_size_bytes, int iterations);

/* Новая: многопоточный доступ к памяти */
double run_ram_multithread_test(long data_size_bytes, int threads);

/* ---------------- DISK Tests ---------------- */

/* Существующие */
double run_disk_write_test(const char* filename, long file_size_bytes);
double run_disk_read_test(const char* filename, long file_size_bytes);

/* Новый: рандомный доступ (random access / IOPS) */
double run_disk_random_access_test(const char* filename, long file_size_bytes, int operations_count);

#ifdef __cplusplus
}
#endif

#endif
