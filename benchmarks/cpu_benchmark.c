#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "benchmarks.h"

typedef struct {
    int iterations;
    volatile double result;
} cpu_thread_data;

/*
 * Высокоточный таймер (Windows)
 */
static double get_time_sec() {
    static LARGE_INTEGER frequency;
    static int freq_initialized = 0;
    if (!freq_initialized) {
        QueryPerformanceFrequency(&frequency);
        freq_initialized = 1;
    }
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)frequency.QuadPart;
}

/*
 * Поток для целочисленных операций.
 */
DWORD WINAPI cpu_int_thread_func(LPVOID arg) {
    cpu_thread_data* data = (cpu_thread_data*)arg;
    int sum = 0;
    for(int i = 0; i < data->iterations; i++) {
        sum += i % 100;
        sum *= 2;
        sum /= 2;
    }
    data->result = (double)sum;
    return 0;
}

/*
 * Поток для float-операций.
 */
DWORD WINAPI cpu_float_thread_func(LPVOID arg) {
    cpu_thread_data* data = (cpu_thread_data*)arg;
    double val = 1.0;
    for(int i = 0; i < data->iterations; i++) {
        val *= 1.000001;
        val /= 1.0000005;
        val += 0.5;
    }
    data->result = val;
    return 0;
}

/*
 * Реализация: run_cpu_integer_ops
 * Запускает целочисленный бенчмарк в нескольких потоках.
 */
double run_cpu_integer_ops(int iterations, int num_threads) {
    HANDLE *threads = NULL;
    cpu_thread_data *thread_data = NULL;

    threads = (HANDLE*)malloc(num_threads * sizeof(HANDLE));
    thread_data = (cpu_thread_data*)malloc(num_threads * sizeof(cpu_thread_data));

    double start_time = get_time_sec();

    // Создаём потоки
    for(int i = 0; i < num_threads; i++) {
        thread_data[i].iterations = iterations;
        thread_data[i].result = 0.0;
        threads[i] = CreateThread(
            NULL, 0, 
            cpu_int_thread_func, 
            &thread_data[i], 
            0, NULL
        );
    }

    WaitForMultipleObjects(num_threads, threads, TRUE, INFINITE);
    double end_time = get_time_sec();

    for(int i = 0; i < num_threads; i++) {
        CloseHandle(threads[i]);
    }
    free(threads);
    free(thread_data);

    return (end_time - start_time);
}

/*
 * Реализация: run_cpu_float_ops
 * Запускает float-бенчмарк в нескольких потоках.
 */
double run_cpu_float_ops(int iterations, int num_threads) {
    HANDLE *threads = NULL;
    cpu_thread_data *thread_data = NULL;

    threads = (HANDLE*)malloc(num_threads * sizeof(HANDLE));
    thread_data = (cpu_thread_data*)malloc(num_threads * sizeof(cpu_thread_data));

    double start_time = get_time_sec();

    for(int i = 0; i < num_threads; i++) {
        thread_data[i].iterations = iterations;
        thread_data[i].result = 0.0;
        threads[i] = CreateThread(
            NULL, 0,
            cpu_float_thread_func,
            &thread_data[i],
            0, NULL
        );
    }

    WaitForMultipleObjects(num_threads, threads, TRUE, INFINITE);
    double end_time = get_time_sec();

    for(int i = 0; i < num_threads; i++) {
        CloseHandle(threads[i]);
    }
    free(threads);
    free(thread_data);

    return (end_time - start_time);
}

/*
 * Пример потока для run_cpu_multithread_load:
 * (смешанная нагрузка int+float)
 */
DWORD WINAPI cpu_mixed_thread_func(LPVOID arg) {
    cpu_thread_data* data = (cpu_thread_data*)arg;
    int sum = 0;
    double val = 1.0;
    for(int i = 0; i < data->iterations; i++) {
        // Integer
        sum += i % 100;
        sum *= 2;
        sum /= 2;
        // Float
        val *= 1.000001;
        val += 0.0001;
    }
    data->result = sum + val;
    return 0;
}

/*
 * Новая функция: run_cpu_multithread_load
 * Запускает смешанную вычислительную нагрузку
 */
double run_cpu_multithread_load(int iterations_per_thread, int num_threads) {
    HANDLE *threads = (HANDLE*)malloc(num_threads * sizeof(HANDLE));
    cpu_thread_data *thread_data = (cpu_thread_data*)malloc(num_threads * sizeof(cpu_thread_data));

    double start_time = get_time_sec();

    for(int i = 0; i < num_threads; i++) {
        thread_data[i].iterations = iterations_per_thread;
        thread_data[i].result = 0.0;
        threads[i] = CreateThread(NULL, 0, cpu_mixed_thread_func, &thread_data[i], 0, NULL);
    }

    WaitForMultipleObjects(num_threads, threads, TRUE, INFINITE);
    double end_time = get_time_sec();

    for(int i = 0; i < num_threads; i++) {
        CloseHandle(threads[i]);
    }
    free(threads);
    free(thread_data);

    return (end_time - start_time);
}
