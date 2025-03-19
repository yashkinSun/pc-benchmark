# file: interface/author_info.py
import tkinter as tk

def show_author_info(parent):
    """
    Показывает окно "Об авторах".
    """
    win = tk.Toplevel(parent)
    win.title("Об авторах")
    win.geometry("400x200")

    lbl = tk.Label(win, text=
    "Данная программа разработана командой:\n"
    " - Иван Иванов\n"
    " - Петр Петров\n"
    " - ...\n\n"
    "Все права защищены © 2025\n",
    justify="left")
    lbl.pack(padx=20, pady=20)

    btn_close = tk.Button(win, text="Закрыть", command=win.destroy)
    btn_close.pack(pady=5)
