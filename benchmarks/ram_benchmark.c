#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "benchmarks.h"

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
 * Реализация (ранее была только extern)
 */
double run_ram_benchmark(long data_size_bytes, int iterations) {
    char* buffer = (char*)malloc(data_size_bytes);
    if (!buffer) {
        fprintf(stderr, "Не удалось выделить память!\n");
        return -1.0;
    }

    double start_time = get_time_sec();

    for(int j = 0; j < iterations; j++) {
        // Запись
        for(long i = 0; i < data_size_bytes; i++) {
            buffer[i] = (char)(i % 256);
        }
        // Чтение
        volatile int temp_sum = 0;
        for(long i = 0; i < data_size_bytes; i++) {
            temp_sum += buffer[i];
        }
    }

    double end_time = get_time_sec();
    free(buffer);

    return (end_time - start_time);
}

/*
 * Новая: тест латентности
 */
double run_ram_latency_test(long data_size_bytes, int iterations) {
    char* buffer = (char*)malloc(data_size_bytes);
    if(!buffer) {
        return -1.0;
    }

    // Инициализируем
    for(long i = 0; i < data_size_bytes; i++) {
        buffer[i] = (char)(i % 256);
    }

    double start_time = get_time_sec();
    // "iterations" раз достаём случайный байт
    for(int iter = 0; iter < iterations; iter++) {
        volatile char tmp = buffer[rand() % data_size_bytes];
        (void)tmp; 
    }
    double end_time = get_time_sec();

    free(buffer);
    return (end_time - start_time);
}

/*
 * Многопоточный RAM
 */
typedef struct {
    char* buffer;
    long data_size_bytes;
    int iterations;
    volatile double result;
} ram_thread_data;

DWORD WINAPI ram_thread_func(LPVOID arg) {
    ram_thread_data* d = (ram_thread_data*)arg;
    volatile int sum = 0;
    for(int i = 0; i < d->iterations; i++) {
        long index = rand() % d->data_size_bytes;
        d->buffer[index] = (char)((d->buffer[index] + i) % 256);
        sum += d->buffer[index];
    }
    d->result = (double)sum;
    return 0;
}

double run_ram_multithread_test(long data_size_bytes, int threads) {
    char* buffer = (char*)malloc(data_size_bytes);
    if(!buffer) {
        return -1.0;
    }

    // Инициализируем
    for(long i = 0; i < data_size_bytes; i++) {
        buffer[i] = (char)(i % 256);
    }

    HANDLE* th = (HANDLE*)malloc(threads * sizeof(HANDLE));
    ram_thread_data* th_data = (ram_thread_data*)malloc(threads * sizeof(ram_thread_data));

    double start_time = get_time_sec();

    // Запускаем потоки
    for(int i = 0; i < threads; i++) {
        th_data[i].buffer = buffer;
        th_data[i].data_size_bytes = data_size_bytes;
        th_data[i].iterations = 1000000; 
        th_data[i].result = 0.0;
        th[i] = CreateThread(NULL, 0, ram_thread_func, &th_data[i], 0, NULL);
    }

    WaitForMultipleObjects(threads, th, TRUE, INFINITE);
    double end_time = get_time_sec();

    for(int i = 0; i < threads; i++) {
        CloseHandle(th[i]);
    }
    free(th);
    free(th_data);
    free(buffer);

    return (end_time - start_time);
}
