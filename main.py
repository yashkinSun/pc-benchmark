import tkinter as tk
from interface.main_gui import BenchmarkGUI

def main():
    root = tk.Tk()
    root.withdraw()  # Скрываем корневое окно, будем работать с Toplevel
    app = BenchmarkGUI(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
