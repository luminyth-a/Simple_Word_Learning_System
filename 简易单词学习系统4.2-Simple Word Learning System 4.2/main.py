import tkinter as tk
from tkinter import messagebox
import sys
import traceback
import os

def show_error_and_exit():
    """显示错误信息并退出（安全版本 - 不泄露路径）"""
    error_msg = traceback.format_exc()
    print(error_msg)  # 完整日志输出到控制台
    
    # 提取错误类型和简要信息（不包含路径）
    error_lines = error_msg.strip().split('\n')
    error_type = ""
    error_detail = ""
    
    for line in error_lines:
        if "Error:" in line or "Exception:" in line:
            # 只提取错误类型，不包含文件路径
            parts = line.split(":")
            if len(parts) >= 2:
                error_type = parts[0].strip()
                error_detail = ":".join(parts[1:]).strip()
                break
    
    if not error_type:
        error_type = "未知错误"
    
    # 安全显示错误信息（修复漏洞7）
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "启动错误", 
        f"程序启动失败：\n\n错误类型: {error_type}\n\n{error_detail}\n\n请检查程序完整性或查看控制台获取详细信息"
    )
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