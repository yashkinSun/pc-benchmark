import platform
import psutil

try:
    import GPUtil
except ImportError:
    GPUtil = None

def get_system_info():
    """
    Собирает и возвращает детальную информацию о ПК
    (ОС, CPU, RAM, Disk, GPU) с помощью psutil, platform, GPUtil.
    """
    info = {}

    # ОС
    info["OS"] = platform.platform()

    # CPU
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    info["CPU"] = platform.processor() or "Unknown CPU"
    info["CPU_Physical_Cores"] = cpu_count_physical
    info["CPU_Logical_Cores"] = cpu_count_logical
    if freq:
        info["CPU_MinFreq_MHz"] = f"{freq.min:.1f}"
        info["CPU_MaxFreq_MHz"] = f"{freq.max:.1f}"

    # RAM
    mem = psutil.virtual_memory()
    total_gb = mem.total / 1024**3
    info["RAM"] = f"{total_gb:.2f} GB total"

    # Disk (берём системный диск)
    partitions = psutil.disk_partitions()
    if partitions:
        sys_disk = partitions[0].device
        usage = psutil.disk_usage(sys_disk)
        total_disk_gb = usage.total / 1024**3
        free_disk_gb = usage.free / 1024**3
        info["Disk"] = f"{sys_disk} : {total_disk_gb:.2f} GB total, {free_disk_gb:.2f} GB free"
    else:
        info["Disk"] = "No disk info"

    # GPU
    if GPUtil:
        gpus = GPUtil.getGPUs()
        if gpus:
            info["GPU"] = gpus[0].name
        else:
            info["GPU"] = "No GPU found"
    else:
        info["GPU"] = "GPUtil not installed"

    return info
