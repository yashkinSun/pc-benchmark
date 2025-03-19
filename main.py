# file: main.py

import tkinter as tk
from interface.main_gui import MainGUI

def main():
    root = tk.Tk()
    root.withdraw()
    app = MainGUI(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
