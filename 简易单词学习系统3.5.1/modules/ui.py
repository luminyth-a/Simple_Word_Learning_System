import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import random
import json
import os
import csv
import sys
from datetime import datetime
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
        self.root.geometry("1100x800")
        self.root.configure(bg="#f5f5f5")
        self.root.minsize(1000, 700)
        
    def init_data(self):
        """初始化数据"""
        self.vocabulary = []
        self.current_index = 0
        self.mode = "study"
        self.show_phonetic = True
        self.theme_mode = "light"
        self.wrong_words = []
        self.load_wrong_words()
    
    def load_wrong_words(self):
        """加载易错词文件"""
        try:
            if getattr(sys, 'frozen', False):
                config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'VocabSystem')
            else:
                config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            os.makedirs(config_dir, exist_ok=True)
            self.wrong_words_file = os.path.join(config_dir, "wrong_words.json")
            
            if os.path.exists(self.wrong_words_file):
                with open(self.wrong_words_file, 'r', encoding='utf-8') as f:
                    self.wrong_words = json.load(f)
        except Exception as e:
            print(f"加载易错词失败: {e}")
            self.wrong_words = []
    
    def save_wrong_words(self):
        """保存易错词 - 使用ensure_ascii=False保持特殊字符"""
        try:
            with open(self.wrong_words_file, 'w', encoding='utf-8') as f:
                json.dump(self.wrong_words, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存易错词失败: {e}")
    
    def add_to_wrong_words(self):
        """将当前单词添加到易错词表（同时保存完整信息）"""
        if not self.vocabulary:
            messagebox.showinfo(
                self.lang.get_text("tips", "提示"), 
                self.lang.get_text("no_word_learning", "没有正在学习的单词")
            )
            return
        
        current_word = self.vocabulary[self.current_index]
        
        # 清理音标中的特殊字符，确保正确保存
        phonetic = current_word.get('phonetic', '')
        
        for word in self.wrong_words:
            if word['english'] == current_word['english']:
                word['wrong_count'] = word.get('wrong_count', 0) + 1
                word['last_wrong_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_wrong_words()
                messagebox.showinfo(
                    self.lang.get_text("tips", "提示"), 
                    f"「{current_word['english']}」{self.lang.get_text('wrong_count_updated', '错误次数已更新')} (+1)"
                )
                return
        
        # 根据是单词还是词组，保存不同的语素/拆解信息
        if current_word.get('is_phrase'):
            root_info = current_word.get('word_meanings', '')
        else:
            root_info = current_word.get('root_info', '')
        
        self.wrong_words.append({
            'english': current_word['english'],
            'phonetic': phonetic,
            'chinese': current_word.get('chinese', ''),
            'root_info': root_info,
            'example': current_word.get('example', ''),
            'example_cn': current_word.get('example_cn', ''),
            'wrong_count': 1,
            'add_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_wrong_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_phrase': current_word.get('is_phrase', False)
        })
        self.save_wrong_words()
        
        # 根据类型显示不同提示
        if current_word.get('is_phrase'):
            messagebox.showinfo(
                self.lang.get_text("tips", "提示"), 
                f"「{current_word['english']}」{self.lang.get_text('added_to_wrong_phrase', '已添加到易错词表（复式）')}"
            )
        else:
            messagebox.showinfo(
                self.lang.get_text("tips", "提示"), 
                f"「{current_word['english']}」{self.lang.get_text('added_to_wrong_word', '已添加到易错词表（单式）')}"
            )
    
    def export_wrong_words_to_csv(self):
        """导出易错词为CSV文件 - 正确处理音标中的特殊字符"""
        if not self.wrong_words:
            messagebox.showinfo(
                self.lang.get_text("tips", "提示"), 
                self.lang.get_text("no_wrong_words", "暂无易错词可导出")
            )
            return
        
        file_path = filedialog.asksaveasfilename(
            title=self.lang.get_text("export_csv", "导出易错词"),
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialfile=f"wrong_words_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow([
                    self.lang.get_text("word", "单词"), 
                    self.lang.get_text("phonetic", "音标"), 
                    self.lang.get_text("meaning", "意思"), 
                    self.lang.get_text("morpheme", "语素/拆解"), 
                    self.lang.get_text("example_sentence", "例句"), 
                    self.lang.get_text("translation", "例句翻译"), 
                    self.lang.get_text("wrong_count", "错误次数")
                ])
                
                for word in sorted(self.wrong_words, key=lambda x: x.get('wrong_count', 0), reverse=True):
                    writer.writerow([
                        word.get('english', ''),
                        word.get('phonetic', ''),
                        word.get('chinese', ''),
                        word.get('root_info', ''),
                        word.get('example', ''),
                        word.get('example_cn', ''),
                        word.get('wrong_count', 0)
                    ])
            
            messagebox.showinfo(
                self.lang.get_text("export_success_title", "导出成功"), 
                self.lang.get_text("export_success", "易错词已导出到：\n{}").format(file_path)
            )
        except Exception as e:
            messagebox.showerror(
                self.lang.get_text("export_failed_title", "导出失败"), 
                self.lang.get_text("export_failed", "导出时发生错误：\n{}").format(str(e))
            )
    
    def view_wrong_words(self):
        """查看易错词表 - 支持多语言"""
        if not self.wrong_words:
            messagebox.showinfo(
                self.lang.get_text("wrong_words_title", "易错词表"), 
                self.lang.get_text("no_wrong_words_record", "暂无易错词记录\n\n学习过程中点击「忘了这个」按钮即可记录")
            )
            return
        
        wrong_window = tk.Toplevel(self.root)
        wrong_window.title(self.lang.get_text("wrong_words_title", "易错词表"))
        wrong_window.geometry("1000x650")
        wrong_window.configure(bg="#f5f5f5")
        
        title_label = ttk.Label(wrong_window, text=self.lang.get_text("wrong_words_title", "📋 易错词表"), 
                               font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)
        
        total_words = len(self.wrong_words)
        total_wrong = sum(w.get('wrong_count', 0) for w in self.wrong_words)
        stats_label = ttk.Label(
            wrong_window, 
            text=self.lang.get_text("wrong_words_stats", "共 {} 个易错词，累计错误 {} 次").format(total_words, total_wrong), 
            font=("微软雅黑", 10), foreground="#7f8c8d"
        )
        stats_label.pack()
        
        # 创建主框架，包含树形视图和详细显示区域
        main_paned = ttk.PanedWindow(wrong_window, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 上部：树形视图框架
        tree_frame = ttk.Frame(main_paned)
        main_paned.add(tree_frame, weight=3)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = (
            self.lang.get_text("word", "单词"), 
            self.lang.get_text("phonetic", "音标"), 
            self.lang.get_text("meaning", "意思"), 
            self.lang.get_text("morpheme", "语素/拆解"), 
            self.lang.get_text("wrong_count", "错误次数"), 
            self.lang.get_text("add_time", "添加时间")
        )
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        col_widths = {"单词": 140, "音标": 150, "意思": 160, "语素/拆解": 220, "错误次数": 80, "添加时间": 140}
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=col_widths.get(list(col_widths.keys())[i] if i < len(col_widths) else 100, 100))
        
        for word in sorted(self.wrong_words, key=lambda x: x.get('wrong_count', 0), reverse=True):
            tree.insert("", "end", values=(
                word.get('english', ''),
                word.get('phonetic', ''),
                word.get('chinese', '')[:50] + "..." if len(word.get('chinese', '')) > 50 else word.get('chinese', ''),
                word.get('root_info', '')[:60] + "..." if len(word.get('root_info', '')) > 60 else word.get('root_info', ''),
                word.get('wrong_count', 0),
                word.get('add_time', '')
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 下部：详细显示区域（例句和翻译）
        detail_frame = ttk.LabelFrame(main_paned, text=self.lang.get_text("detail_info", "详细信息"), padding="10")
        main_paned.add(detail_frame, weight=1)
        
        detail_text = tk.Text(detail_frame, wrap=tk.WORD, font=("微软雅黑", 10), height=5)
        detail_text.pack(fill=tk.BOTH, expand=True)
        
        def on_tree_select(event):
            selected = tree.selection()
            if selected:
                values = tree.item(selected[0])['values']
                english = values[0]
                for word in self.wrong_words:
                    if word.get('english') == english:
                        detail_text.delete(1.0, tk.END)
                        detail_text.insert(tk.END, f"【{self.lang.get_text('example_sentence', '例句')}】\n{word.get('example', self.lang.get_text('none', '无'))}\n\n")
                        detail_text.insert(tk.END, f"【{self.lang.get_text('translation', '翻译')}】\n{word.get('example_cn', self.lang.get_text('none', '无'))}\n\n")
                        if word.get('is_phrase'):
                            detail_text.insert(tk.END, f"【{self.lang.get_text('word_breakdown', '单词拆解')}】\n{word.get('root_info', self.lang.get_text('none', '无'))}")
                        else:
                            detail_text.insert(tk.END, f"【{self.lang.get_text('root_analysis', '词根分析')}】\n{word.get('root_info', self.lang.get_text('none', '无'))}")
                        break
        
        tree.bind('<<TreeviewSelect>>', on_tree_select)
        
        btn_frame = ttk.Frame(wrong_window)
        btn_frame.pack(pady=10)
        
        def export_to_csv():
            self.export_wrong_words_to_csv()
        
        def clear_wrong_words():
            if messagebox.askyesno(
                self.lang.get_text("confirm", "确认"), 
                self.lang.get_text("confirm_clear", "确定要清空所有易错词记录吗？")
            ):
                self.wrong_words = []
                self.save_wrong_words()
                wrong_window.destroy()
                messagebox.showinfo(
                    self.lang.get_text("tips", "提示"), 
                    self.lang.get_text("cleared", "易错词表已清空")
                )
        
        def remove_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo(
                    self.lang.get_text("tips", "提示"), 
                    self.lang.get_text("select_word_first", "请先选择要删除的单词")
                )
                return
            
            for item in selected:
                values = tree.item(item)['values']
                if values:
                    for i, word in enumerate(self.wrong_words):
                        if word.get('english') == values[0]:
                            del self.wrong_words[i]
                            break
            
            self.save_wrong_words()
            wrong_window.destroy()
            self.view_wrong_words()
        
        ttk.Button(btn_frame, text=self.lang.get_text("export_csv", "📁 导出CSV"), 
                  command=export_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self.lang.get_text("delete_selected", "🗑️ 删除选中"), 
                  command=remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self.lang.get_text("clear_all", "🗑️ 清空全部"), 
                  command=clear_wrong_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self.lang.get_text("close", "关闭"), 
                  command=wrong_window.destroy).pack(side=tk.LEFT, padx=5)
    
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
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)
        
        # 标题 - 使用StringVar实现动态更新
        self.title_var = tk.StringVar()
        self.title_var.set(self.lang.get_text("app_title", "简易背单词软件"))
        title_label = ttk.Label(header_frame, textvariable=self.title_var, 
                               font=("微软雅黑", 16, "bold"), foreground="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=4, pady=5)
        
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        self.phonetic_toggle_btn = ttk.Button(right_frame, text=self.lang.get_text("phonetic_on", "🔊 音标:开"), 
                                             command=self.toggle_phonetic)
        self.phonetic_toggle_btn.pack(side=tk.LEFT, padx=5)
        
        self.create_language_menu(right_frame)
        
        self.theme_btn = ttk.Button(right_frame, text=self.lang.get_text("dark_mode", "🌙 暗色模式"), 
                                   command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_wrong_btn = ttk.Button(right_frame, text=self.lang.get_text("wrong_words_list", "📋 易错词表"), 
                                        command=self.view_wrong_words)
        self.view_wrong_btn.pack(side=tk.LEFT, padx=5)
    
    def create_language_menu(self, parent):
        """创建语言切换菜单"""
        languages = self.lang.get_language_list()
        
        if languages:
            # 创建标签并保存为实例变量
            self.lang_label = ttk.Label(parent, text=self.lang.get_text("language", "🌐 语言:"), font=("微软雅黑", 9))
            self.lang_label.pack(side=tk.LEFT, padx=5)
            
            lang_names = [name for code, name in languages]
            max_len = max(len(name) for name in lang_names)
            dropdown_width = max(10, min(max_len + 2, 20))
            
            self.language_var = tk.StringVar()
            current_name = self.lang.get_text("language_name", "简体中文")
            self.language_var.set(current_name)
            
            self.language_menu = ttk.Combobox(parent, textvariable=self.language_var, 
                                              values=lang_names,
                                              state="readonly", width=dropdown_width, font=("微软雅黑", 9))
            self.language_menu.pack(side=tk.LEFT, padx=5)
            
            self.language_map = {name: code for code, name in languages}
            self.language_menu.bind('<<ComboboxSelected>>', self.on_language_changed)
    
    def on_language_changed(self, event=None):
        """语言切换回调"""
        selected_name = self.language_var.get()
        selected_code = self.language_map.get(selected_name, "zh-CN")
        
        if self.lang.save_language(selected_code):
            self.refresh_ui_texts()
    
    def refresh_ui_texts(self):
        """刷新所有界面文本"""
        # 更新窗口标题
        self.root.title(self.lang.get_text("app_title", "简易背单词软件"))
        
        # 更新标题栏标题
        self.title_var.set(self.lang.get_text("app_title", "简易背单词软件"))
        
        # 更新标题栏按钮
        self.phonetic_toggle_btn.config(text=self.lang.get_text("phonetic_on" if self.show_phonetic else "phonetic_off", 
                                                                "🔊 音标:开" if self.show_phonetic else "🔇 音标:关"))
        self.theme_btn.config(text=self.lang.get_text("dark_mode" if self.theme_mode == "light" else "light_mode", 
                                                      "🌙 暗色模式" if self.theme_mode == "light" else "☀️ 亮色模式"))
        
        # 更新易错词表按钮
        self.view_wrong_btn.config(text=self.lang.get_text("wrong_words_list", "📋 易错词表"))
        
        # 更新语言标签文字
        if hasattr(self, 'lang_label'):
            self.lang_label.config(text=self.lang.get_text("language", "🌐 语言:"))
        
        self.refresh_mode_selector()
        self.refresh_control_buttons()
        
        self.quiz_label.config(text=self.lang.get_text("quiz_label", "请输入英文单词/词组:"))
        self.check_btn.config(text=self.lang.get_text("check_answer", "✅ 检查答案"))
        self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"))
        
        self.refresh_language_menu()
        
        # 刷新例句显示（让例句和翻译的标签也更新）
        if self.vocabulary:
            self.show_example()
            self.show_details_info()
        
        self.update_display()
    
    def refresh_language_menu(self):
        """刷新语言下拉菜单"""
        languages = self.lang.get_language_list()
        if languages:
            lang_names = [name for code, name in languages]
            current_name = self.lang.get_text("language_name", "简体中文")
            self.language_menu['values'] = lang_names
            self.language_var.set(current_name)
            self.language_map = {name: code for code, name in languages}
    
    def refresh_mode_selector(self):
        """刷新模式选择器"""
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
            btn.pack(side=tk.LEFT, padx=6)
    
    def refresh_control_buttons(self):
        """刷新控制面板按钮"""
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        
        file_frame = ttk.Frame(self.control_frame)
        file_frame.pack(pady=5)
        
        ttk.Button(file_frame, text=self.lang.get_text("import_csv", "📁 导入CSV"), 
                  command=self.import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text=self.lang.get_text("shuffle", "🔄 随机打乱"), 
                  command=self.shuffle_words).pack(side=tk.LEFT, padx=5)
        
        # 忘记按钮 - 从语言文件读取文字
        self.forgot_btn = ttk.Button(file_frame, text=self.lang.get_text("forgot_word", "📌 忘了这个"), 
                                     command=self.add_to_wrong_words)
        self.forgot_btn.pack(side=tk.LEFT, padx=5)
        
        nav_frame = ttk.Frame(self.control_frame)
        nav_frame.pack(pady=5)
        
        ttk.Button(nav_frame, text=self.lang.get_text("previous", "⬅️ 上一个"), 
                  command=self.prev_word).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text=self.lang.get_text("next", "下一个 ➡️"), 
                  command=self.next_word).pack(side=tk.LEFT, padx=5)
    
    def create_mode_selector(self):
        """创建模式选择器"""
        self.mode_frame = ttk.LabelFrame(self.main_frame, text=self.lang.get_text("select_mode", "选择学习模式"), padding="10")
        self.mode_frame.pack(fill=tk.X, pady=(0, 10))
        
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
            btn.pack(side=tk.LEFT, padx=6)
    
    def create_word_card(self):
        """创建单词卡片 - 使用支持音标的字体"""
        self.card_frame = ttk.LabelFrame(self.main_frame, text=self.lang.get_text("study_content", "学习内容"), padding="15")
        self.card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        center_container = ttk.Frame(self.card_frame)
        center_container.pack(expand=True, fill=tk.BOTH)
        
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
        
        content_frame = ttk.Frame(self.scrollable_frame)
        content_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # 单词显示
        self.word_label = ttk.Label(content_frame, text="", 
                                   font=("Arial", 28, "bold"), foreground="#2c3e50", 
                                   wraplength=800, justify="center")
        self.word_label.pack(pady=(5, 3))
        
        # 音标显示 - 使用支持国际音标的字体 Lucida Sans Unicode
        self.phonetic_label = ttk.Label(content_frame, text="", 
                                       font=("Lucida Sans Unicode", 13, "italic"), foreground="#7f8c8d")
        self.phonetic_label.pack(pady=3)
        
        # 发音按钮
        self.speak_btn = ttk.Button(content_frame, text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), 
                                   command=self.speak_current, width=14)
        self.speak_btn.pack(pady=5)
        
        # 中文意思显示
        self.chinese_label = ttk.Label(content_frame, text="", 
                                      font=("微软雅黑", 16), foreground="#34495e", 
                                      wraplength=800, justify="center")
        self.chinese_label.pack(pady=5)
        
        # 语素/词根/词组拆解显示
        self.details_frame = tk.Frame(content_frame, bg="#FFF8DC", relief="solid", bd=1)
        self.details_frame.pack(pady=8, fill=tk.X, padx=40)
        
        self.details_label = tk.Label(self.details_frame, text="", 
                                     font=("微软雅黑", 10, "bold"), 
                                     fg="#8B4513",
                                     bg="#FFF8DC",
                                     wraplength=750,
                                     justify=tk.CENTER,
                                     padx=10,
                                     pady=6)
        self.details_label.pack(fill=tk.BOTH, expand=True)
        
        # 例句显示区域
        self.example_frame = tk.Frame(content_frame, bg="#E8F8F5", relief="solid", bd=1)
        self.example_frame.pack(pady=8, fill=tk.X, padx=40)
        
        self.example_label = tk.Label(self.example_frame, text="", 
                                     font=("微软雅黑", 10), 
                                     fg="#1B5E20",
                                     bg="#E8F8F5",
                                     wraplength=750,
                                     justify=tk.LEFT,
                                     padx=10,
                                     pady=6)
        self.example_label.pack(fill=tk.BOTH, expand=True)
        
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
                                   font=("微软雅黑", 10))
        self.quiz_label.grid(row=0, column=0, padx=(0, 10), sticky="e")
        
        self.quiz_entry = ttk.Entry(input_frame, font=("Arial", 12), width=25)
        self.quiz_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.quiz_entry.bind("<Return>", self.check_answer)
        
        self.check_btn = ttk.Button(input_frame, text=self.lang.get_text("check_answer", "✅ 检查答案"), 
                                   command=self.check_answer, width=12)
        self.check_btn.grid(row=0, column=2)
        
        self.quiz_feedback = ttk.Label(self.quiz_frame, text="", 
                                      font=("微软雅黑", 10))
        self.quiz_feedback.pack(pady=5)
        
        self.quiz_frame.pack_forget()
    
    def create_control_panel(self):
        """创建控制面板"""
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=5)
        
        self.refresh_control_buttons()
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text=self.lang.get_text("status_welcome", "👋 欢迎使用简易背单词软件"), 
                                     font=("微软雅黑", 8), foreground="#7f8c8d")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.count_label = ttk.Label(status_frame, text="0/0", 
                                    font=("微软雅黑", 8), foreground="#7f8c8d")
        self.count_label.grid(row=0, column=1, padx=8)
        
        self.progress = ttk.Progressbar(status_frame, length=150, mode='determinate')
        self.progress.grid(row=0, column=2, sticky="e")
    
    def switch_mode(self, mode):
        """切换学习模式"""
        self.mode = mode
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
            self.add_to_wrong_words()
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
            file_type = self.lang.get_text("phrase_type", "词组") if self.vocabulary and self.vocabulary[0].get('is_phrase') else self.lang.get_text("word_type", "单词")
            self.status_label.config(text=self.lang.get_text("import_success", "✅ 成功导入 {} 个{}").format(len(self.vocabulary), file_type))
        except Exception as e:
            messagebox.showerror(
                self.lang.get_text("import_error", "导入错误"), 
                f"{self.lang.get_text('import_failed', '导入失败')}：\n{str(e)}"
            )
    
    def load_sample_words(self):
        """加载示例单式"""
        content = CSVReader.generate_sample_word_csv()
        self.load_from_content(content, self.lang.get_text("word_type", "单词"))
    
    def load_sample_phrases(self):
        """加载示例复式"""
        content = CSVReader.generate_sample_phrase_csv()
        self.load_from_content(content, self.lang.get_text("phrase_type", "词组"))
    
    def load_from_content(self, content, file_type):
        """从内容加载数据"""
        lines = content.strip().split('\n')
        vocabulary = []
        
        for line in lines[1:]:
            parts = CSVReader.parse_csv_line(line)
            if len(parts) >= 2:
                if file_type == self.lang.get_text("phrase_type", "词组"):
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
        """显示详细信息（语素或单词拆解）"""
        if not self.vocabulary:
            return
        
        word = self.vocabulary[self.current_index]
        
        if word.get('is_phrase'):
            if word.get('word_meanings'):
                self.details_frame.pack(pady=8, fill=tk.X, padx=40)
                self.details_label.config(
                    text=self.lang.get_text("phrase_prefix", "📖 单词拆解: ") + word['word_meanings'],
                    fg="#8B4513",
                    bg="#FFF8DC"
                )
            else:
                self.details_frame.pack_forget()
        else:
            if word.get('root_info'):
                self.details_frame.pack(pady=8, fill=tk.X, padx=40)
                self.details_label.config(
                    text=self.lang.get_text("root_prefix", "🌱 ") + word['root_info'],
                    fg="#8B4513",
                    bg="#FFF8DC",
                    font=("微软雅黑", 10, "bold")
                )
            else:
                self.details_frame.pack_forget()
    
    def show_example(self):
        """显示例句（英文 + 中文翻译）- 支持多语言标签"""
        if not self.vocabulary:
            return
        
        word = self.vocabulary[self.current_index]
        example_en = word.get('example', '')
        example_cn = word.get('example_cn', '')
        
        # 获取当前语言对应的标签文字
        example_label_text = self.lang.get_text("example_sentence", "例句")
        translation_label_text = self.lang.get_text("translation", "翻译")
        
        if example_en and example_cn:
            self.example_frame.pack(pady=8, fill=tk.X, padx=40)
            self.example_label.config(
                text=f"📖 {example_label_text}：\n{example_en}\n\n📝 {translation_label_text}：{example_cn}",
                fg="#1B5E20",
                bg="#E8F8F5",
                font=("微软雅黑", 10)
            )
        elif example_en:
            self.example_frame.pack(pady=8, fill=tk.X, padx=40)
            self.example_label.config(
                text=f"📖 {example_label_text}：\n{example_en}",
                fg="#1B5E20",
                bg="#E8F8F5",
                font=("微软雅黑", 10)
            )
        else:
            self.example_frame.pack_forget()
    
    def update_display(self):
        """根据当前模式更新显示"""
        if not self.vocabulary:
            self.show_welcome()
            return
        
        word = self.vocabulary[self.current_index]
        
        self.speak_btn.config(command=self.speak_current)
        
        if self.mode == "study":
            # 学习模式：显示所有内容
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            phonetic_text = word['phonetic'] if self.show_phonetic else ""
            self.phonetic_label.config(text=phonetic_text, font=("Lucida Sans Unicode", 13, "italic"))
            self.chinese_label.config(text=word['chinese'], foreground="#34495e")
            self.show_details_info()
            self.show_example()
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), state="normal")
            
        elif self.mode == "listen":
            self.word_label.config(text="🎧 ???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=self.lang.get_text("listen_hint", "🎧 点击下方按钮听发音，然后在弹出的对话框中输入单词"), foreground="#e74c3c", font=("微软雅黑", 11))
            self.details_frame.pack_forget()
            self.example_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("listen_and_guess", "🎧 播放发音并猜词"), command=self.listen_and_guess, state="normal")
            
        elif self.mode == "speak":
            self.word_label.config(text="???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.example_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("play_standard", "🔊 播放标准发音"), command=self.speak_current)
            
        elif self.mode == "read":
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            phonetic_text = word['phonetic'] if self.show_phonetic else ""
            self.phonetic_label.config(text=phonetic_text, font=("Lucida Sans Unicode", 13, "italic"))
            self.chinese_label.config(text="???", foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.example_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), command=self.speak_current)
            
        elif self.mode == "write":
            self.word_label.config(text="✏️ " + self.lang.get_text("write_mode", "请默写"), foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            self.details_frame.pack_forget()
            self.example_frame.pack_forget()
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 听发音提示"), command=self.speak_current)
            self.quiz_label.config(text=self.lang.get_text("quiz_label", "请输入英文单词/词组:"))
        
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
        
        answer = simpledialog.askstring(
            self.lang.get_text("listening_test", "听力测试"), 
            self.lang.get_text("listen_question", "播放的单词/词组是什么？\n提示: {} 个字符").format(len(word['english'])),
            parent=self.root
        )
        
        if answer:
            if answer.strip().lower() == word['english'].lower():
                messagebox.showinfo(
                    self.lang.get_text("listening_test", "听力测试"), 
                    self.lang.get_text("correct_answer", "✅ 回答正确！")
                )
                self.status_label.config(text=self.lang.get_text("correct_answer", "✅ 听力练习正确: ") + word['english'])
                self.root.after(1500, self.next_word)
            else:
                messagebox.showinfo(
                    self.lang.get_text("listening_test", "听力测试"), 
                    self.lang.get_text("wrong_answer", "❌ 回答错误！\n正确答案: {}\n你的答案: {}").format(word['english'], answer)
                )
                self.status_label.config(text=self.lang.get_text("wrong", "❌ 听力练习错误，正确答案是: ") + word['english'])
                self.add_to_wrong_words()
        else:
            self.status_label.config(text=self.lang.get_text("answer_is", "答案: {}").format(word['english']))
    
    def show_welcome(self):
        """显示欢迎界面 - 简洁版，无CSV格式说明"""
        self.word_label.config(text=self.lang.get_text("welcome_title", "📚 欢迎使用简易背单词软件"), foreground="#2c3e50")
        self.phonetic_label.config(text="")
        self.chinese_label.config(text=self.lang.get_text("welcome_subtitle", "点击上方按钮导入CSV文件开始学习"), foreground="#34495e", font=("微软雅黑", 14))
        
        # 隐藏详情和例句区域，显示简单提示
        self.details_frame.pack(pady=8, fill=tk.X, padx=40)
        self.details_label.config(
            text=self.lang.get_text("tip_text", "💡 提示：\n\n• 点击【导入CSV】可加载自己的语言学习文件\n• 语素信息会以醒目颜色显示\n• 例句包含英文和中文翻译\n• 点击【忘了这个】可记录易错词"),
            fg="#2c3e50",
            bg="#ECF0F1",
            font=("微软雅黑", 10),
            justify=tk.LEFT
        )
        self.example_frame.pack_forget()
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
            self.details_label.config(bg="#3d2b1f", fg="#FFD700")
            self.details_frame.config(bg="#3d2b1f")
            self.example_label.config(bg="#1a3a2a", fg="#a5d6a7")
            self.example_frame.config(bg="#1a3a2a")
        else:
            self.theme_mode = "light"
            self.theme_btn.config(text=self.lang.get_text("dark_mode", "🌙 暗色模式"))
            self.root.configure(bg="#f5f5f5")
            self.status_label.config(foreground="#7f8c8d")
            self.details_label.config(bg="#FFF8DC", fg="#8B4513")
            self.details_frame.config(bg="#FFF8DC")
            self.example_label.config(bg="#E8F8F5", fg="#1B5E20")
            self.example_frame.config(bg="#E8F8F5")