# file: utils/system_info.py

import platform

def get_system_info():
    """
    Возвращает словарь со сведениями о ПК:
    - Модель CPU (platform.processor())
    - Информация о ОС
    - (Заглушки) по RAM, Disk, GPU, если нужно
    """
    info = {}
    info["OS"] = platform.platform()
    info["CPU"] = platform.processor() or "Не удалось определить CPU"
    
    # Простейшие "заглушки" для RAM, Disk, GPU.
    # Для реальной информации нужны дополнительные методы (WMI и т.п.).
    info["RAM"] = "8 GB (пример)"
    info["Disk"] = "Samsung 512GB (пример)"
    info["GPU"] = "NVIDIA GeForce (пример)"

    return info
