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
 * Реализация run_disk_write_test
 */
double run_disk_write_test(const char* filename, long file_size_bytes) {
    FILE *fp = fopen(filename, "wb");
    if(!fp) {
        fprintf(stderr, "Не удалось открыть файл для записи!\n");
        return -1.0;
    }

    size_t block_size = 1024 * 1024; // 1MB
    char *buffer = (char*)malloc(block_size);
    if(!buffer) {
        fclose(fp);
        fprintf(stderr, "Не удалось выделить память!\n");
        return -1.0;
    }

    for(size_t i = 0; i < block_size; i++) {
        buffer[i] = (char)(i % 256);
    }

    double start_time = get_time_sec();

    long total_written = 0;
    while(total_written < file_size_bytes) {
        long to_write = file_size_bytes - total_written;
        if(to_write > (long)block_size) {
            to_write = (long)block_size;
        }
        fwrite(buffer, 1, (size_t)to_write, fp);
        total_written += to_write;
    }

    fflush(fp);
    fclose(fp);

    double end_time = get_time_sec();
    free(buffer);

    return (end_time - start_time);
}

/*
 * Реализация run_disk_read_test
 */
double run_disk_read_test(const char* filename, long file_size_bytes) {
    FILE *fp = fopen(filename, "rb");
    if(!fp) {
        fprintf(stderr, "Не удалось открыть файл для чтения!\n");
        return -1.0;
    }

    size_t block_size = 1024 * 1024; // 1MB
    char *buffer = (char*)malloc(block_size);
    if(!buffer) {
        fclose(fp);
        fprintf(stderr, "Не удалось выделить память!\n");
        return -1.0;
    }

    double start_time = get_time_sec();
    long total_read = 0;
    while(total_read < file_size_bytes) {
        long remaining = file_size_bytes - total_read;
        size_t to_read = (remaining < (long)block_size) ? remaining : block_size;
        size_t actually_read = fread(buffer, 1, to_read, fp);
        if(actually_read == 0) {
            break;
        }
        total_read += (long)actually_read;
    }

    fclose(fp);
    double end_time = get_time_sec();

    free(buffer);
    return (end_time - start_time);
}

/*
 * Новый тест - random access
 */
double run_disk_random_access_test(const char* filename, long file_size_bytes, int operations_count) {
    // Создаём файл
    FILE* fp = fopen(filename, "wb");
    if(!fp) return -1.0;

    char filler = 0xAA;
    for(long i = 0; i < file_size_bytes; i++) {
        fwrite(&filler, 1, 1, fp);
    }
    fclose(fp);

    // Открываем на чтение-запись
    fp = fopen(filename, "rb+");
    if(!fp) return -1.0;

    char buffer[4096];
    for(int i = 0; i < 4096; i++) {
        buffer[i] = (char)(rand() % 256);
    }

    double start_time = get_time_sec();

    for(int i = 0; i < operations_count; i++) {
        long offset = rand() % (file_size_bytes - 4096);
        fseek(fp, offset, SEEK_SET);

        if(i % 2 == 0) {
            fread(buffer, 1, 4096, fp);
        } else {
            fwrite(buffer, 1, 4096, fp);
        }
    }

    double end_time = get_time_sec();
    fclose(fp);
    return (end_time - start_time);
}
