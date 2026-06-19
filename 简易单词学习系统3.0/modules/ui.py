import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import random
import sys
import os
from modules.csv_reader import CSVReader
from modules.tts import TextToSpeech
from modules.language_manager import LanguageManager


class VocabUI:
    def __init__(self, root):
        self.root = root
        self.lang = LanguageManager()
        self.setup_window()
        self.init_data()
        self.init_modules()
        self.create_ui()
        self.update_display()
    
    def setup_window(self):
        """设置窗口"""
        self.root.title(self.lang.get_text("app_title", "简易背单词软件"))
        self.root.geometry("1200x850")
        self.root.configure(bg="#f5f5f5")
        self.root.minsize(1050, 750)
        
    def init_data(self):
        """初始化数据"""
        self.vocabulary = []
        self.current_index = 0
        self.mode = "study"
        self.show_phonetic = True
        self.theme_mode = "light"
        
    def init_modules(self):
        """初始化模块"""
        self.tts = TextToSpeech()
    
    def create_ui(self):
        """创建界面"""
        self.create_main_frame()
        self.create_header()
        self.create_mode_selector()
        self.create_word_card()
        self.create_quiz_panel()
        self.create_control_panel()
        self.create_status_bar()
    
    def create_main_frame(self):
        """创建主框架"""
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)
    
    def create_header(self):
        """创建标题栏"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # 标题居中
        title_label = ttk.Label(header_frame, text=self.lang.get_text("app_title", "简易背单词软件"), 
                               font=("微软雅黑", 18, "bold"), foreground="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=4, pady=5)
        
        # 右侧按钮放在独立行
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        self.phonetic_toggle_btn = ttk.Button(right_frame, text=self.lang.get_text("phonetic_on", "🔊 音标:开"), 
                                             command=self.toggle_phonetic)
        self.phonetic_toggle_btn.pack(side=tk.LEFT, padx=8)
        
        # 语言切换按钮
        self.create_language_menu(right_frame)
        
        self.theme_btn = ttk.Button(right_frame, text=self.lang.get_text("dark_mode", "🌙 暗色模式"), 
                                   command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=8)
    
    def create_language_menu(self, parent):
        """创建语言切换菜单"""
        languages = self.lang.get_language_list()
        
        if languages:
            # 创建标签
            lang_label = ttk.Label(parent, text=self.lang.get_text("language", "🌐 语言:"), font=("微软雅黑", 10))
            lang_label.pack(side=tk.LEFT, padx=5)
            
            # 获取语言名称列表
            lang_names = [name for code, name in languages]
            
            # 计算最长语言名称的宽度
            max_len = max(len(name) for name in lang_names)
            dropdown_width = max(12, min(max_len + 2, 25))
            
            # 创建下拉菜单
            self.language_var = tk.StringVar()
            # 获取当前语言名称
            current_name = self.lang.get_text("language_name", "简体中文")
            self.language_var.set(current_name)
            
            self.language_menu = ttk.Combobox(parent, textvariable=self.language_var, 
                                              values=lang_names,
                                              state="readonly", width=dropdown_width, font=("微软雅黑", 10))
            self.language_menu.pack(side=tk.LEFT, padx=5)
            
            # 存储语言代码映射
            self.language_map = {name: code for code, name in languages}
            
            # 绑定切换事件
            self.language_menu.bind('<<ComboboxSelected>>', self.on_language_changed)
    
    def on_language_changed(self, event=None):
        """语言切换回调"""
        selected_name = self.language_var.get()
        selected_code = self.language_map.get(selected_name, "zh-CN")
        
        if self.lang.save_language(selected_code):
            # 刷新界面文本
            self.refresh_ui_texts()
    
    def refresh_ui_texts(self):
        """刷新所有界面文本"""
        # 更新窗口标题
        self.root.title(self.lang.get_text("app_title", "简易背单词软件"))
        
        # 更新标题栏按钮
        self.phonetic_toggle_btn.config(text=self.lang.get_text("phonetic_on" if self.show_phonetic else "phonetic_off", 
                                                                "🔊 音标:开" if self.show_phonetic else "🔇 音标:关"))
        self.theme_btn.config(text=self.lang.get_text("dark_mode" if self.theme_mode == "light" else "light_mode", 
                                                      "🌙 暗色模式" if self.theme_mode == "light" else "☀️ 亮色模式"))
        
        # 更新模式选择器
        self.refresh_mode_selector()
        
        # 更新控制面板按钮
        self.refresh_control_buttons()
        
        # 更新默写面板
        self.quiz_label.config(text=self.lang.get_text("quiz_label", "请输入英文单词/词组:"))
        self.check_btn.config(text=self.lang.get_text("check_answer", "✅ 检查答案"))
        
        # 更新发音按钮
        self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"))
        
        # 更新语言下拉菜单
        self.refresh_language_menu()
        
        # 更新显示
        self.update_display()
    
    def refresh_language_menu(self):
        """刷新语言下拉菜单"""
        languages = self.lang.get_language_list()
        if languages:
            lang_names = [name for code, name in languages]
            current_name = self.lang.get_text("language_name", "简体中文")
            self.language_menu['values'] = lang_names
            self.language_var.set(current_name)
            # 更新映射
            self.language_map = {name: code for code, name in languages}
    
    def refresh_mode_selector(self):
        """刷新模式选择器"""
        # 重新创建模式选择器
        for widget in self.mode_frame.winfo_children():
            widget.destroy()
        
        center_frame = ttk.Frame(self.mode_frame)
        center_frame.pack()
        
        modes = [
            (self.lang.get_text("study_mode", "📖 学习模式"), "study"),
            (self.lang.get_text("listen_mode", "👂 听力模式"), "listen"),
            (self.lang.get_text("speak_mode", "🗣️ 口语模式"), "speak"),
            (self.lang.get_text("read_mode", "📖 阅读模式"), "read"),
            (self.lang.get_text("write_mode", "✏️ 默写模式"), "write")
        ]
        
        for text, mode in modes:
            btn = ttk.Button(center_frame, text=text, 
                           command=lambda m=mode: self.switch_mode(m))
            btn.pack(side=tk.LEFT, padx=8)
    
    def refresh_control_buttons(self):
        """刷新控制面板按钮"""
        # 重新创建控制面板
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        
        # 文件操作 - 居中
        file_frame = ttk.Frame(self.control_frame)
        file_frame.pack(pady=8)
        
        ttk.Button(file_frame, text=self.lang.get_text("import_csv", "📁 导入CSV"), 
                  command=self.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text=self.lang.get_text("shuffle", "🔄 随机打乱"), 
                  command=self.shuffle_words).pack(side=tk.LEFT, padx=5)
        
        # 导航按钮 - 居中
        nav_frame = ttk.Frame(self.control_frame)
        nav_frame.pack(pady=8)
        
        ttk.Button(nav_frame, text=self.lang.get_text("previous", "⬅️ 上一个"), 
                  command=self.prev_word).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text=self.lang.get_text("next", "下一个 ➡️"), 
                  command=self.next_word).pack(side=tk.LEFT, padx=5)
    
    def create_mode_selector(self):
        """创建模式选择器"""
        self.mode_frame = ttk.LabelFrame(self.main_frame, text=self.lang.get_text("select_mode", "选择学习模式"), padding="15")
        self.mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 让按钮居中
        center_frame = ttk.Frame(self.mode_frame)
        center_frame.pack()
        
        modes = [
            (self.lang.get_text("study_mode", "📖 学习模式"), "study"),
            (self.lang.get_text("listen_mode", "👂 听力模式"), "listen"),
            (self.lang.get_text("speak_mode", "🗣️ 口语模式"), "speak"),
            (self.lang.get_text("read_mode", "📖 阅读模式"), "read"),
            (self.lang.get_text("write_mode", "✏️ 默写模式"), "write")
        ]
        
        for text, mode in modes:
            btn = ttk.Button(center_frame, text=text, 
                           command=lambda m=mode: self.switch_mode(m))
            btn.pack(side=tk.LEFT, padx=8)
    
    def create_word_card(self):
        """创建单词卡片"""
        self.card_frame = ttk.LabelFrame(self.main_frame, text=self.lang.get_text("study_content", "学习内容"), padding="20")
        self.card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 创建居中容器
        center_container = ttk.Frame(self.card_frame)
        center_container.pack(expand=True, fill=tk.BOTH)
        
        # 使用Canvas和Scrollbar支持滚动
        canvas_frame = ttk.Frame(center_container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 内容居中框架
        content_frame = ttk.Frame(self.scrollable_frame)
        content_frame.pack(expand=True, fill=tk.BOTH, pady=20)
        
        # 单词显示
        self.word_label = ttk.Label(content_frame, text="", 
                                   font=("Arial", 38, "bold"), foreground="#2c3e50", 
                                   wraplength=850, justify="center")
        self.word_label.pack(pady=(10, 5))
        
        # 音标显示
        self.phonetic_label = ttk.Label(content_frame, text="", 
                                       font=("Arial", 16, "italic"), foreground="#7f8c8d")
        self.phonetic_label.pack(pady=5)
        
        # 发音按钮
        self.speak_btn = ttk.Button(content_frame, text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), 
                                   command=self.speak_current)
        self.speak_btn.pack(pady=12)
        
        # 中文显示
        self.chinese_label = ttk.Label(content_frame, text="", 
                                      font=("微软雅黑", 18), foreground="#34495e", 
                                      wraplength=850, justify="center")
        self.chinese_label.pack(pady=10)
        
        # 词根/单词意思显示 - 使用醒目的颜色
        self.details_frame = tk.Frame(content_frame, bg="#FFF8DC", relief="solid", bd=1)
        self.details_frame.pack(pady=10, fill=tk.X, padx=50)
        
        self.details_label = tk.Label(self.details_frame, text="", 
                                     font=("微软雅黑", 12, "bold"), 
                                     fg="#8B4513",
                                     bg="#FFF8DC",
                                     wraplength=750,
                                     justify=tk.CENTER,
                                     padx=15,
                                     pady=10)
        self.details_label.pack(fill=tk.BOTH, expand=True)
        
        # 绑定窗口大小变化事件
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        if not self.tts.available:
            self.speak_btn.config(state="disabled", text="🔇 语音不可用")
    
    def _on_canvas_configure(self, event):
        """Canvas大小变化时更新内容宽度"""
        self.canvas.itemconfig(1, width=event.width - 20)
    
    def create_quiz_panel(self):
        """创建默写/答题面板"""
        self.quiz_frame = ttk.Frame(self.main_frame)
        self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(self.quiz_frame)
        input_frame.pack(fill=tk.X, pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        self.quiz_label = ttk.Label(input_frame, text=self.lang.get_text("quiz_label", "请输入英文单词/词组:"), 
                                   font=("微软雅黑", 11))
        self.quiz_label.grid(row=0, column=0, padx=(0, 10), sticky="e")
        
        self.quiz_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.quiz_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.quiz_entry.bind("<Return>", self.check_answer)
        
        self.check_btn = ttk.Button(input_frame, text=self.lang.get_text("check_answer", "✅ 检查答案"), 
                                   command=self.check_answer)
        self.check_btn.grid(row=0, column=2)
        
        self.quiz_feedback = ttk.Label(self.quiz_frame, text="", 
                                      font=("微软雅黑", 11))
        self.quiz_feedback.pack(pady=5)
        
        self.quiz_frame.pack_forget()
    
    def create_control_panel(self):
        """创建控制面板"""
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.refresh_control_buttons()
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text=self.lang.get_text("status_welcome", "👋 欢迎使用简易背单词软件"), 
                                     font=("微软雅黑", 9), foreground="#7f8c8d")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.count_label = ttk.Label(status_frame, text="0/0", 
                                    font=("微软雅黑", 9), foreground="#7f8c8d")
        self.count_label.grid(row=0, column=1, padx=10)
        
        self.progress = ttk.Progressbar(status_frame, length=180, mode='determinate')
        self.progress.grid(row=0, column=2, sticky="e")
    
    def switch_mode(self, mode):
        """切换学习模式"""
        self.mode = mode
        # 重置发音按钮的命令
        self.speak_btn.config(command=self.speak_current)
        self.update_display()
        
        if mode == "write":
            self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
            self.quiz_entry.focus()
        else:
            self.quiz_frame.pack_forget()
            self.quiz_entry.delete(0, tk.END)
            self.quiz_feedback.config(text="")
        
        mode_names = {
            "study": self.lang.get_text("mode_study", "学习模式"), 
            "listen": self.lang.get_text("mode_listen", "听力模式"), 
            "speak": self.lang.get_text("mode_speak", "口语模式"), 
            "read": self.lang.get_text("mode_read", "阅读模式"), 
            "write": self.lang.get_text("mode_write", "默写模式")
        }
        self.status_label.config(text=self.lang.get_text("mode_switched", "🎯 {} - 开始学习吧！").format(mode_names.get(mode, mode)))
    
    def toggle_phonetic(self):
        """切换音标显示"""
        self.show_phonetic = not self.show_phonetic
        self.phonetic_toggle_btn.config(text=self.lang.get_text("phonetic_on" if self.show_phonetic else "phonetic_off", 
                                                                "🔊 音标:开" if self.show_phonetic else "🔇 音标:关"))
        self.update_display()
    
    def speak_current(self):
        """播放当前单词/词组发音"""
        if not self.vocabulary or not self.tts.available:
            return
        word = self.vocabulary[self.current_index]
        self.tts.speak(word['english'])
        self.status_label.config(text=self.lang.get_text("playing", "🔊 正在播放: {}").format(word['english']))
    
    def check_answer(self, event=None):
        """检查答案（默写模式）"""
        if not self.vocabulary:
            return
        
        user_answer = self.quiz_entry.get().strip().lower()
        correct_answer = self.vocabulary[self.current_index]['english'].lower()
        
        if not user_answer:
            self.quiz_feedback.config(text=self.lang.get_text("please_input", "⚠️ 请输入答案"), foreground="#f39c12")
            return
        
        if user_answer == correct_answer:
            self.quiz_feedback.config(text=self.lang.get_text("correct", "✅ 回答正确！"), foreground="#27ae60")
            self.root.after(1000, self.next_word)
            self.root.after(1000, lambda: self.quiz_entry.delete(0, tk.END))
            self.root.after(1000, lambda: self.quiz_feedback.config(text=""))
        else:
            self.quiz_feedback.config(text=self.lang.get_text("wrong", "❌ 错误！正确答案: ") + correct_answer, 
                                     foreground="#e74c3c")
            self.quiz_entry.delete(0, tk.END)
            self.quiz_entry.focus()
    
    def import_csv(self):
        """导入CSV文件"""
        file_path = filedialog.askopenfilename(
            title=self.lang.get_text("import_csv", "选择单词文件"),
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")])
        
        if not file_path:
            return
        
        try:
            self.vocabulary = CSVReader.read_csv(file_path)
            self.current_index = 0
            self.switch_mode("study")
            self.update_display()
            file_type = self.lang.get_text("phrase_type", "复式") if self.vocabulary and self.vocabulary[0].get('is_phrase') else self.lang.get_text("word_type", "单式")
            self.status_label.config(text=self.lang.get_text("import_success", "✅ 成功导入 {} 个{}").format(len(self.vocabulary), file_type))
        except Exception as e:
            messagebox.showerror(self.lang.get_text("import_csv", "导入错误"), f"导入失败：\n{str(e)}")
    
    def load_sample_words(self):
        """加载示例单式"""
        content = CSVReader.generate_sample_word_csv()
        self.load_from_content(content, self.lang.get_text("word_type", "单式"))
    
    def load_sample_phrases(self):
        """加载示例复式"""
        content = CSVReader.generate_sample_phrase_csv()
        self.load_from_content(content, self.lang.get_text("phrase_type", "复式"))
    
    def load_from_content(self, content, file_type):
        """从内容加载数据"""
        lines = content.strip().split('\n')
        vocabulary = []
        
        for line in lines[1:]:
            parts = CSVReader.parse_csv_line(line)
            if len(parts) >= 2:
                if file_type == self.lang.get_text("phrase_type", "复式"):
                    item = CSVReader.process_phrase_format(parts)
                else:
                    item = CSVReader.process_word_format(parts)
                if item:
                    vocabulary.append(item)
        
        if vocabulary:
            self.vocabulary = vocabulary
            self.current_index = 0
            self.switch_mode("study")
            self.update_display()
            self.status_label.config(text=self.lang.get_text("load_success", "✅ 已加载 {} 个示例{}").format(len(vocabulary), file_type))
    
    def shuffle_words(self):
        """随机打乱"""
        if self.vocabulary:
            random.shuffle(self.vocabulary)
            self.current_index = 0
            self.update_display()
            self.status_label.config(text=self.lang.get_text("shuffle_success", "🔀 单词顺序已打乱"))
    
    def prev_word(self):
        """上一个"""
        if self.vocabulary:
            self.current_index = (self.current_index - 1) % len(self.vocabulary)
            self.quiz_entry.delete(0, tk.END)
            self.quiz_feedback.config(text="")
            self.update_display()
    
    def next_word(self):
        """下一个"""
        if self.vocabulary:
            self.current_index = (self.current_index + 1) % len(self.vocabulary)
            self.quiz_entry.delete(0, tk.END)
            self.quiz_feedback.config(text="")
            self.update_display()
    
    def show_details_info(self):
        """显示详细信息（语素或单式拆解）- 使用醒目颜色"""
        word = self.vocabulary[self.current_index]
        
        # 显示/隐藏详细解释框架
        if word.get('is_phrase'):
            if word.get('word_meanings'):
                self.details_frame.pack(pady=10, fill=tk.X, padx=50)
                self.details_label.config(
                    text=self.lang.get_text("phrase_prefix", "📖 单式拆解: ") + word['word_meanings'],
                    fg="#8B4513",
                    bg="#FFF8DC"
                )
            else:
                self.details_frame.pack_forget()
        else:
            # 优先显示完整的语素信息
            if word.get('root_info'):
                self.details_frame.pack(pady=10, fill=tk.X, padx=50)
                self.details_label.config(
                    text=self.lang.get_text("root_prefix", "🌱 ") + word['root_info'],
                    fg="#8B4513",
                    bg="#FFF8DC",
                    font=("微软雅黑", 12, "bold")
                )
            elif word.get('root_word') and word.get('root_meaning'):
                self.details_frame.pack(pady=10, fill=tk.X, padx=50)
                self.details_label.config(
                    text=self.lang.get_text("root_prefix", "🌱 语素: ") + word['root_word'] + " — " + word['root_meaning'],
                    fg="#8B4513",
                    bg="#FFF8DC",
                    font=("微软雅黑", 12, "bold")
                )
            elif word.get('root_word'):
                self.details_frame.pack(pady=10, fill=tk.X, padx=50)
                self.details_label.config(
                    text=self.lang.get_text("root_prefix", "🌱 语素: ") + word['root_word'],
                    fg="#8B4513",
                    bg="#FFF8DC",
                    font=("微软雅黑", 12, "bold")
                )
            elif word.get('root_meaning'):
                self.details_frame.pack(pady=10, fill=tk.X, padx=50)
                self.details_label.config(
                    text=self.lang.get_text("root_prefix", "🌱 语素意思: ") + word['root_meaning'],
                    fg="#8B4513",
                    bg="#FFF8DC",
                    font=("微软雅黑", 12, "bold")
                )
            else:
                self.details_frame.pack_forget()
    
    def update_display(self):
        """根据当前模式更新显示"""
        if not self.vocabulary:
            self.show_welcome()
            return
        
        word = self.vocabulary[self.current_index]
        
        # 重置发音按钮命令（防止残留）
        self.speak_btn.config(command=self.speak_current)
        
        if self.mode == "study":
            # 学习模式：显示所有内容
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            self.phonetic_label.config(text=word['phonetic'] if self.show_phonetic else "")
            self.chinese_label.config(text=word['chinese'], foreground="#34495e")
            self.show_details_info()
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), state="normal")
            
        elif self.mode == "listen":
            # 听力模式：隐藏所有内容
            self.word_label.config(text="🎧 ???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=self.lang.get_text("listen_hint", "🎧 点击下方按钮听发音，然后在弹出的对话框中输入单词"), foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("listen_and_guess", "🎧 播放发音并猜词"), command=self.listen_and_guess, state="normal")
            
        elif self.mode == "speak":
            # 口语模式：只显示中文
            self.word_label.config(text="???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("play_standard", "🔊 播放标准发音"), command=self.speak_current)
            
        elif self.mode == "read":
            # 阅读模式：只显示英文
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            self.phonetic_label.config(text=word['phonetic'] if self.show_phonetic else "")
            self.chinese_label.config(text="???", foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), command=self.speak_current)
            
        elif self.mode == "write":
            # 默写模式：只显示中文意思，不显示语素
            self.word_label.config(text="✏️ " + self.lang.get_text("write_mode", "请默写"), foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 听发音提示"), command=self.speak_current)
            self.quiz_label.config(text=self.lang.get_text("quiz_label", "请输入英文单词/词组:"))
        
        # 音标显示控制
        if self.mode != "listen" and not self.show_phonetic:
            self.phonetic_label.config(text="")
        
        self.update_status()
    
    def listen_and_guess(self):
        """听力模式：播放发音并让用户猜词"""
        if not self.vocabulary:
            return
        
        word = self.vocabulary[self.current_index]
        self.tts.speak(word['english'])
        self.status_label.config(text=self.lang.get_text("listening_played", "🔊 已播放，请猜词..."))
        
        # 弹出输入框
        answer = simpledialog.askstring(
            self.lang.get_text("listening_test", "听力测试"), 
            self.lang.get_text("listen_question", "播放的单词/词组是什么？\n提示: {} 个字符").format(len(word['english'])),
            parent=self.root
        )
        
        if answer:
            if answer.strip().lower() == word['english'].lower():
                messagebox.showinfo(self.lang.get_text("listening_test", "结果"), self.lang.get_text("correct_answer", "✅ 回答正确！"))
                self.status_label.config(text=self.lang.get_text("correct_answer", "✅ 听力练习正确: ") + word['english'])
                self.root.after(1500, self.next_word)
            else:
                messagebox.showinfo(self.lang.get_text("listening_test", "结果"), 
                                   self.lang.get_text("wrong_answer", "❌ 回答错误！\n正确答案: {}\n你的答案: {}").format(word['english'], answer))
                self.status_label.config(text=self.lang.get_text("wrong", "❌ 听力练习错误，正确答案是: ") + word['english'])
        else:
            # 用户取消，显示答案
            self.status_label.config(text=self.lang.get_text("answer_is", "答案: {}").format(word['english']))
    
    def show_welcome(self):
        """显示欢迎界面 - 使用详细的示例格式"""
        self.word_label.config(text=self.lang.get_text("welcome_title", "📚 欢迎使用简易背单词软件"), foreground="#2c3e50")
        self.phonetic_label.config(text="")
        self.chinese_label.config(text=self.lang.get_text("welcome_subtitle", "点击上方按钮导入CSV文件或加载示例开始学习"), foreground="#34495e")
        
        # 显示格式说明
        self.details_frame.pack(pady=10, fill=tk.X, padx=50)
        
        # 构建格式说明文本
        format_text = (
            self.lang.get_text("csv_format_title", "📖 CSV文件格式说明\n\n") +
            self.lang.get_text("word_format", "【单式格式】4列：单式（一个字/一个单词）,音标,意思,语素\n") +
            self.lang.get_text("word_example1", "structured,['strʌktʃəd],adj.结构化的；有条理的,词根struct-（建造、构筑）；后缀-ure（名词后缀）；后缀-ed（形容词后缀）\n") +
            self.lang.get_text("word_example2", "visible,/'vɪzəbl/,adj. 可见的,词根vid-（看）；后缀-ible（可...的）\n\n") +
            self.lang.get_text("phrase_format", "【复式格式】4列：复式（多个字/多个单词组成）,音标,意思,组成复式的单式和意思\n") +
            self.lang.get_text("phrase_example1", "table salt,/'teɪbl sɔːlt/,食用盐,table (n. 桌子；餐桌) + salt (n. 盐)\n") +
            self.lang.get_text("phrase_example2", "look forward to,/lʊk 'fɔːrwərd tuː/,期待,look (看) + forward (向前) + to (到)\n\n") +
            self.lang.get_text("tip_text", "💡 提示：\n• 点击【导入CSV】可加载自己的单词文件\n• 语素信息会以醒目颜色显示")
        )
        
        self.details_label.config(
            text=format_text,
            fg="#2c3e50",
            bg="#ECF0F1",
            font=("微软雅黑", 11),
            justify=tk.LEFT
        )
        self.speak_btn.config(state="disabled")
        self.progress['value'] = 0
        self.count_label.config(text="0/0")
    
    def update_status(self):
        """更新状态栏"""
        if not self.vocabulary:
            total = 0
            current = 0
        else:
            total = len(self.vocabulary)
            current = self.current_index + 1
        
        progress = (current / total * 100) if total > 0 else 0
        self.count_label.config(text=f"{current}/{total}")
        self.progress['value'] = progress
    
    def toggle_theme(self):
        """切换主题"""
        if self.theme_mode == "light":
            self.theme_mode = "dark"
            self.theme_btn.config(text=self.lang.get_text("light_mode", "☀️ 亮色模式"))
            self.root.configure(bg="#2c3e50")
            self.status_label.config(foreground="#bdc3c7")
            # 更新语素标签背景
            self.details_label.config(bg="#3d2b1f", fg="#FFD700")
            self.details_frame.config(bg="#3d2b1f")
        else:
            self.theme_mode = "light"
            self.theme_btn.config(text=self.lang.get_text("dark_mode", "🌙 暗色模式"))
            self.root.configure(bg="#f5f5f5")
            self.status_label.config(foreground="#7f8c8d")
            # 恢复语素标签背景
            self.details_label.config(bg="#FFF8DC", fg="#8B4513")
            self.details_frame.config(bg="#FFF8DC")