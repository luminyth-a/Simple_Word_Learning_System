import tkinter as tk
import sys
import os

# 添加路径支持（打包后使用）
if getattr(sys, 'frozen', False):
    # 打包后的路径
    base_path = sys._MEIPASS
else:
    # 开发环境路径
    base_path = os.path.dirname(os.path.abspath(__file__))

# 添加modules路径
sys.path.insert(0, os.path.join(base_path, 'modules'))

from modules.ui import VocabUI

def main():
    root = tk.Tk()
    app = VocabUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()