import tkinter as tk
from modules.ui import VocabUI

def main():
    root = tk.Tk()
    app = VocabUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()