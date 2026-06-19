import tkinter as tk
from tkinter import messagebox
import sys
import traceback

def show_error_and_exit():
    """显示错误信息并退出"""
    error_msg = traceback.format_exc()
    print(error_msg)
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showerror("启动错误", f"程序启动失败：\n\n{error_msg}\n\n请检查文件是否完整")
    root.destroy()
    sys.exit(1)

if __name__ == "__main__":
    try:
        from modules.ui import VocabUI
        
        root = tk.Tk()
        app = VocabUI(root)
        root.mainloop()
    except Exception as e:
        show_error_and_exit()