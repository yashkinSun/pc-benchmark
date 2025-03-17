#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "benchmarks.h"

/*
 * Высокоточный замер времени на Windows
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
 * Простая реализация RAM-бенчмарка:
 * - Выделяем буфер data_size_bytes
 * - Многократно пишем туда данные
 * - Многократно читаем и суммируем
 */
double run_ram_benchmark(long data_size_bytes, int iterations) {
    char *buffer = NULL;
    buffer = (char*)malloc(data_size_bytes);
    if(!buffer) {
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
