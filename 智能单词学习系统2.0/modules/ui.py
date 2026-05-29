import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import random
from modules.csv_reader import CSVReader
from modules.tts import TextToSpeech

class VocabUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.init_data()
        self.init_modules()
        self.create_ui()
        self.update_display()
    
    def setup_window(self):
        """设置窗口"""
        self.root.title("智能单词学习系统 - 听说读写全能版")
        self.root.geometry("1000x750")
        self.root.configure(bg="#f5f5f5")
        self.root.minsize(900, 650)
        
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
        
        title_label = ttk.Label(header_frame, text="📚 智能单词学习系统 - 听说读写全能版", 
                               font=("微软雅黑", 16, "bold"), foreground="#2c3e50")
        title_label.grid(row=0, column=0, sticky="w")
        
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=0, column=1, sticky="e")
        
        self.phonetic_toggle_btn = ttk.Button(right_frame, text="🔊 音标:开", 
                                             command=self.toggle_phonetic, width=10)
        self.phonetic_toggle_btn.pack(side=tk.LEFT, padx=3)
        
        self.theme_btn = ttk.Button(right_frame, text="🌙 暗色模式", 
                                   command=self.toggle_theme, width=10)
        self.theme_btn.pack(side=tk.LEFT, padx=3)
        
        header_frame.columnconfigure(0, weight=1)
    
    def create_mode_selector(self):
        """创建模式选择器"""
        mode_frame = ttk.LabelFrame(self.main_frame, text="学习模式", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        modes = [
            ("📖 学习模式", "study", "完整显示所有内容"),
            ("👂 听力模式", "listen", "听发音猜单词"),
            ("🗣️ 口语模式", "speak", "看中文说英文"),
            ("📖 阅读模式", "read", "看英文理解意思"),
            ("✏️ 默写模式", "write", "根据意思默写")
        ]
        
        for text, mode, tip in modes:
            btn = ttk.Button(mode_frame, text=text, 
                           command=lambda m=mode: self.switch_mode(m),
                           width=14)
            btn.pack(side=tk.LEFT, padx=5)
            
            tip_label = ttk.Label(mode_frame, text=tip, font=("微软雅黑", 8), foreground="#7f8c8d")
            tip_label.pack(side=tk.LEFT, padx=(0, 10))
    
    def create_word_card(self):
        """创建单词卡片"""
        self.card_frame = ttk.LabelFrame(self.main_frame, text="学习内容", padding="25")
        self.card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        content_frame = ttk.Frame(self.card_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 单词显示
        self.word_label = ttk.Label(content_frame, text="", 
                                   font=("Arial", 32, "bold"), foreground="#2c3e50")
        self.word_label.pack(pady=(10, 5))
        
        # 音标显示
        self.phonetic_label = ttk.Label(content_frame, text="", 
                                       font=("Arial", 14, "italic"), foreground="#7f8c8d")
        self.phonetic_label.pack(pady=5)
        
        # 发音按钮
        self.speak_btn = ttk.Button(content_frame, text="🔊 播放发音", 
                                   command=self.speak_current, width=12)
        self.speak_btn.pack(pady=5)
        
        # 中文显示
        self.chinese_label = ttk.Label(content_frame, text="", 
                                      font=("微软雅黑", 16), foreground="#34495e")
        self.chinese_label.pack(pady=10)
        
        # 词根/单词意思显示
        self.details_label = ttk.Label(content_frame, text="", 
                                      font=("微软雅黑", 11), 
                                      foreground="#95a5a6",
                                      wraplength=600,
                                      justify=tk.CENTER)
        self.details_label.pack(pady=5)
        
        if not self.tts.available:
            self.speak_btn.config(state="disabled", text="🔇 语音不可用")
    
    def create_quiz_panel(self):
        """创建默写/答题面板"""
        self.quiz_frame = ttk.Frame(self.main_frame)
        self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(self.quiz_frame)
        input_frame.pack(fill=tk.X, pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        self.quiz_label = ttk.Label(input_frame, text="请输入答案:", 
                                   font=("微软雅黑", 11))
        self.quiz_label.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.quiz_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.quiz_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.quiz_entry.bind("<Return>", self.check_answer)
        
        self.check_btn = ttk.Button(input_frame, text="✅ 检查答案", 
                                   command=self.check_answer, width=12)
        self.check_btn.grid(row=0, column=2)
        
        self.quiz_feedback = ttk.Label(self.quiz_frame, text="", 
                                      font=("微软雅黑", 11))
        self.quiz_feedback.pack(pady=5)
        
        self.quiz_frame.pack_forget()
    
    def create_control_panel(self):
        """创建控制面板"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # 文件操作
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(pady=5)
        
        ttk.Button(file_frame, text="📁 导入CSV", 
                  command=self.import_csv, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(file_frame, text="🔄 随机打乱", 
                  command=self.shuffle_words, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(file_frame, text="📝 示例单词", 
                  command=self.load_sample_words, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(file_frame, text="📝 示例词组", 
                  command=self.load_sample_phrases, width=12).pack(side=tk.LEFT, padx=3)
        
        # 导航按钮
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(pady=5)
        
        ttk.Button(nav_frame, text="⬅️ 上一个", 
                  command=self.prev_word, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(nav_frame, text="下一个 ➡️", 
                  command=self.next_word, width=12).pack(side=tk.LEFT, padx=3)
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="👋 欢迎使用单词学习系统", 
                                     font=("微软雅黑", 9), foreground="#7f8c8d")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.count_label = ttk.Label(status_frame, text="0/0", 
                                    font=("微软雅黑", 9), foreground="#7f8c8d")
        self.count_label.grid(row=0, column=1, padx=10)
        
        self.progress = ttk.Progressbar(status_frame, length=150, mode='determinate')
        self.progress.grid(row=0, column=2)
    
    def switch_mode(self, mode):
        """切换学习模式"""
        self.mode = mode
        self.update_display()
        
        if mode == "write":
            self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
            self.quiz_entry.focus()
        else:
            self.quiz_frame.pack_forget()
            self.quiz_entry.delete(0, tk.END)
            self.quiz_feedback.config(text="")
        
        mode_names = {"study": "学习模式", "listen": "听力模式", 
                     "speak": "口语模式", "read": "阅读模式", "write": "默写模式"}
        self.status_label.config(text=f"🎯 {mode_names.get(mode, mode)} - 开始学习吧！")
    
    def toggle_phonetic(self):
        """切换音标显示"""
        self.show_phonetic = not self.show_phonetic
        self.phonetic_toggle_btn.config(text="🔊 音标:开" if self.show_phonetic else "🔇 音标:关")
        self.update_display()
    
    def speak_current(self):
        """播放当前单词/词组发音"""
        if not self.vocabulary or not self.tts.available:
            return
        word = self.vocabulary[self.current_index]
        self.tts.speak(word['english'])
        self.status_label.config(text=f"🔊 正在播放: {word['english']}")
    
    def check_answer(self, event=None):
        """检查答案（默写模式）"""
        if not self.vocabulary:
            return
        
        user_answer = self.quiz_entry.get().strip().lower()
        correct_answer = self.vocabulary[self.current_index]['english'].lower()
        
        if not user_answer:
            self.quiz_feedback.config(text="⚠️ 请输入答案", foreground="#f39c12")
            return
        
        if user_answer == correct_answer:
            self.quiz_feedback.config(text="✅ 回答正确！", foreground="#27ae60")
            self.root.after(1000, self.next_word)
            self.root.after(1000, lambda: self.quiz_entry.delete(0, tk.END))
            self.root.after(1000, lambda: self.quiz_feedback.config(text=""))
        else:
            self.quiz_feedback.config(text=f"❌ 错误！正确答案: {correct_answer}", 
                                     foreground="#e74c3c")
            self.quiz_entry.delete(0, tk.END)
            self.quiz_entry.focus()
    
    def import_csv(self):
        """导入CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择单词文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")])
        
        if not file_path:
            return
        
        try:
            self.vocabulary = CSVReader.read_csv(file_path)
            self.current_index = 0
            self.switch_mode("study")
            self.update_display()
            file_type = "词组" if self.vocabulary and self.vocabulary[0].get('is_phrase') else "单词"
            self.status_label.config(text=f"✅ 成功导入 {len(self.vocabulary)} 个{file_type}")
        except Exception as e:
            messagebox.showerror("导入错误", f"导入失败：\n{str(e)}")
    
    def load_sample_words(self):
        """加载示例单词"""
        content = CSVReader.generate_sample_word_csv()
        self.load_from_content(content, "单词")
    
    def load_sample_phrases(self):
        """加载示例词组"""
        content = CSVReader.generate_sample_phrase_csv()
        self.load_from_content(content, "词组")
    
    def load_from_content(self, content, file_type):
        """从内容加载数据"""
        lines = content.strip().split('\n')
        vocabulary = []
        
        for line in lines[1:]:
            parts = CSVReader.parse_csv_line(line)
            if len(parts) >= 2:
                if file_type == "词组":
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
            self.status_label.config(text=f"✅ 已加载 {len(vocabulary)} 个示例{file_type}")
    
    def shuffle_words(self):
        """随机打乱"""
        if self.vocabulary:
            random.shuffle(self.vocabulary)
            self.current_index = 0
            self.update_display()
            self.status_label.config(text="🔀 单词顺序已打乱")
    
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
        """显示详细信息（词根或单词意思）"""
        word = self.vocabulary[self.current_index]
        if word.get('is_phrase'):
            if word.get('word_meanings'):
                self.details_label.config(text=f"📖 单词拆解: {word['word_meanings']}")
            else:
                self.details_label.config(text="")
        else:
            if word.get('root_word') and word.get('root_meaning'):
                self.details_label.config(text=f"🌱 词根: {word['root_word']} — {word['root_meaning']}")
            elif word.get('root_word'):
                self.details_label.config(text=f"🌱 词根: {word['root_word']}")
            elif word.get('root_meaning'):
                self.details_label.config(text=f"🌱 词根意思: {word['root_meaning']}")
            else:
                self.details_label.config(text="")
    
    def update_display(self):
        """根据当前模式更新显示"""
        if not self.vocabulary:
            self.show_welcome()
            return
        
        word = self.vocabulary[self.current_index]
        
        if self.mode == "study":
            # 学习模式：显示所有内容
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            self.phonetic_label.config(text=word['phonetic'] if self.show_phonetic else "")
            self.chinese_label.config(text=word['chinese'], foreground="#34495e")
            self.show_details_info()
            self.speak_btn.config(text="🔊 播放发音", state="normal")
            
        elif self.mode == "listen":
            # 听力模式：隐藏所有内容
            self.word_label.config(text="🎧 ???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text="点击下方按钮听发音，猜猜是什么单词/词组", foreground="#e74c3c")
            self.details_label.config(text="")
            self.speak_btn.config(text="🎧 播放发音并猜词", command=self.listen_and_guess)
            
        elif self.mode == "speak":
            # 口语模式：只显示中文
            self.word_label.config(text="???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            self.details_label.config(text="🗣️ 请说出对应的英文单词/词组，然后点击播放发音对照", foreground="#27ae60")
            self.speak_btn.config(text="🔊 播放标准发音", command=self.speak_current)
            
        elif self.mode == "read":
            # 阅读模式：只显示英文
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            self.phonetic_label.config(text=word['phonetic'] if self.show_phonetic else "")
            self.chinese_label.config(text="???", foreground="#e74c3c")
            self.details_label.config(text="📖 请理解这个单词/词组的意思，然后点击播放发音", foreground="#27ae60")
            self.speak_btn.config(text="🔊 播放发音", command=self.speak_current)
            
        elif self.mode == "write":
            # 默写模式：只显示中文意思，不显示词根
            self.word_label.config(text="✏️ 请默写", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            # 默写模式不显示词根信息
            self.details_label.config(text="💡 根据上方中文意思默写英文单词/词组", foreground="#27ae60")
            self.speak_btn.config(text="🔊 听发音提示", command=self.speak_current)
            self.quiz_label.config(text="请输入英文单词/词组:")
        
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
        self.status_label.config(text=f"🔊 已播放，请猜词...")
        
        # 弹出输入框
        answer = simpledialog.askstring("听力测试", 
                                       f"播放的单词/词组是什么？\n提示: {len(word['english'])} 个字符",
                                       parent=self.root)
        
        if answer:
            if answer.strip().lower() == word['english'].lower():
                messagebox.showinfo("结果", "✅ 回答正确！")
                self.status_label.config(text=f"✅ 听力练习正确: {word['english']}")
                self.root.after(1500, self.next_word)
            else:
                messagebox.showinfo("结果", f"❌ 回答错误！\n正确答案: {word['english']}\n你的答案: {answer}")
                self.status_label.config(text=f"❌ 听力练习错误，正确答案是: {word['english']}")
        else:
            # 用户取消，显示答案
            self.status_label.config(text=f"答案: {word['english']}")
    
    def show_welcome(self):
        """显示欢迎界面"""
        self.word_label.config(text="📚 单词学习系统", foreground="#2c3e50")
        self.phonetic_label.config(text="")
        self.chinese_label.config(text="点击'导入CSV'或'示例单词'开始学习", foreground="#34495e")
        self.details_label.config(text="支持格式:\n单词: 单词,音标,意思,词根(词根 意思)\n词组: 词组,音标,意思,单词意思", 
                                 foreground="#95a5a6")
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
            self.theme_btn.config(text="☀️ 亮色模式")
            self.root.configure(bg="#2c3e50")
            self.status_label.config(foreground="#bdc3c7")
        else:
            self.theme_mode = "light"
            self.theme_btn.config(text="🌙 暗色模式")
            self.root.configure(bg="#f5f5f5")
            self.status_label.config(foreground="#7f8c8d")