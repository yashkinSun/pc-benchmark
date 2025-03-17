#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "benchmarks.h"

/*
 * Структура для передачи параметров в поток.
 */
typedef struct {
    int iterations;
    volatile double result;
} cpu_thread_data;

/*
 * Функция для высокоточного замера времени на Windows
 * с помощью QueryPerformanceCounter.
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
 * Функция потока для целочисленных операций.
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
    return 0; // код завершения потока
}

/*
 * Функция потока для операций с плавающей точкой.
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
 * Запуск целочисленного бенчмарка CPU в нескольких потоках
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
            NULL,          // атрибуты безопасности
            0,             // размер стека (по умолчанию)
            cpu_int_thread_func, // функция потока
            &thread_data[i],     // передаваемые данные
            0,             // флаги создания
            NULL           // идентификатор потока
        );
    }

    // Ждём, пока все потоки закончат
    WaitForMultipleObjects(num_threads, threads, TRUE, INFINITE);

    double end_time = get_time_sec();

    // Закрываем дескрипторы потоков
    for(int i = 0; i < num_threads; i++) {
        CloseHandle(threads[i]);
    }

    free(threads);
    free(thread_data);

    return (end_time - start_time);
}

/*
 * Запуск бенчмарка с плавающей точкой CPU в нескольких потоках
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
            NULL,
            0,
            cpu_float_thread_func,
            &thread_data[i],
            0,
            NULL
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
