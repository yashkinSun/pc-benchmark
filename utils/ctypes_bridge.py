import ctypes
import os
import platform

if platform.system() == "Windows":
    lib_name = "benchmarks.dll"
elif platform.system() == "Darwin":
    lib_name = "libbenchmarks.dylib"
else:
    lib_name = "libbenchmarks.so"

LIB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "benchmarks",
    lib_name
)

benchmarks_lib = ctypes.cdll.LoadLibrary(LIB_PATH)

# Существующие CPU
benchmarks_lib.run_cpu_integer_ops.argtypes = [ctypes.c_int, ctypes.c_int]
benchmarks_lib.run_cpu_integer_ops.restype = ctypes.c_double

benchmarks_lib.run_cpu_float_ops.argtypes = [ctypes.c_int, ctypes.c_int]
benchmarks_lib.run_cpu_float_ops.restype = ctypes.c_double

# Новый CPU test
benchmarks_lib.run_cpu_multithread_load.argtypes = [ctypes.c_int, ctypes.c_int]
benchmarks_lib.run_cpu_multithread_load.restype = ctypes.c_double

# Существующий RAM
benchmarks_lib.run_ram_benchmark.argtypes = [ctypes.c_long, ctypes.c_int]
benchmarks_lib.run_ram_benchmark.restype = ctypes.c_double

# Новые RAM tests
benchmarks_lib.run_ram_latency_test.argtypes = [ctypes.c_long, ctypes.c_int]
benchmarks_lib.run_ram_latency_test.restype = ctypes.c_double

benchmarks_lib.run_ram_multithread_test.argtypes = [ctypes.c_long, ctypes.c_int]
benchmarks_lib.run_ram_multithread_test.restype = ctypes.c_double

# Существующие DISK
benchmarks_lib.run_disk_write_test.argtypes = [ctypes.c_char_p, ctypes.c_long]
benchmarks_lib.run_disk_write_test.restype = ctypes.c_double

benchmarks_lib.run_disk_read_test.argtypes = [ctypes.c_char_p, ctypes.c_long]
benchmarks_lib.run_disk_read_test.restype = ctypes.c_double

# Новый Disk test
benchmarks_lib.run_disk_random_access_test.argtypes = [ctypes.c_char_p, ctypes.c_long, ctypes.c_int]
benchmarks_lib.run_disk_random_access_test.restype = ctypes.c_double

def cpu_integer_test(iterations, threads):
    return benchmarks_lib.run_cpu_integer_ops(iterations, threads)

def cpu_float_test(iterations, threads):
    return benchmarks_lib.run_cpu_float_ops(iterations, threads)

def cpu_multithread_load_test(iterations_per_thread, threads):
    return benchmarks_lib.run_cpu_multithread_load(iterations_per_thread, threads)

def ram_test(data_size_bytes, iterations):
    return benchmarks_lib.run_ram_benchmark(data_size_bytes, iterations)

def ram_latency_test(data_size_bytes, iterations):
    return benchmarks_lib.run_ram_latency_test(data_size_bytes, iterations)

def ram_multithread_test(data_size_bytes, threads):
    return benchmarks_lib.run_ram_multithread_test(data_size_bytes, threads)

def disk_write_test(filename, size_bytes):
    return benchmarks_lib.run_disk_write_test(filename.encode('utf-8'), size_bytes)

def disk_read_test(filename, size_bytes):
    return benchmarks_lib.run_disk_read_test(filename.encode('utf-8'), size_bytes)

def disk_random_access_test(filename, size_bytes, ops_count):
    return benchmarks_lib.run_disk_random_access_test(filename.encode('utf-8'), size_bytes, ops_count)
