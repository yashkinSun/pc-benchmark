import ctypes
import os
import platform

# Путь к скомпилированной библиотеке
# Предполагается, что после компиляции она будет называться "libbenchmarks.so" (Linux) 
# или "benchmarks.dll" (Windows), или "libbenchmarks.dylib" (macOS).
# Здесь нужно подставить реальное имя файла библиотеки.
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

# Настраиваем сигнатуры функций
# double run_cpu_integer_ops(int iterations, int num_threads);
benchmarks_lib.run_cpu_integer_ops.argtypes = [ctypes.c_int, ctypes.c_int]
benchmarks_lib.run_cpu_integer_ops.restype = ctypes.c_double

# double run_cpu_float_ops(int iterations, int num_threads);
benchmarks_lib.run_cpu_float_ops.argtypes = [ctypes.c_int, ctypes.c_int]
benchmarks_lib.run_cpu_float_ops.restype = ctypes.c_double

# double run_ram_benchmark(long data_size_bytes, int iterations);
benchmarks_lib.run_ram_benchmark.argtypes = [ctypes.c_long, ctypes.c_int]
benchmarks_lib.run_ram_benchmark.restype = ctypes.c_double

# double run_disk_write_test(const char* filename, long file_size_bytes);
benchmarks_lib.run_disk_write_test.argtypes = [ctypes.c_char_p, ctypes.c_long]
benchmarks_lib.run_disk_write_test.restype = ctypes.c_double

# double run_disk_read_test(const char* filename, long file_size_bytes);
benchmarks_lib.run_disk_read_test.argtypes = [ctypes.c_char_p, ctypes.c_long]
benchmarks_lib.run_disk_read_test.restype = ctypes.c_double

def cpu_integer_test(iterations, threads):
    return benchmarks_lib.run_cpu_integer_ops(iterations, threads)

def cpu_float_test(iterations, threads):
    return benchmarks_lib.run_cpu_float_ops(iterations, threads)

def ram_test(data_size_bytes, iterations):
    return benchmarks_lib.run_ram_benchmark(data_size_bytes, iterations)

def disk_write_test(filename, size_bytes):
    return benchmarks_lib.run_disk_write_test(filename.encode('utf-8'), size_bytes)

def disk_read_test(filename, size_bytes):
    return benchmarks_lib.run_disk_read_test(filename.encode('utf-8'), size_bytes)
