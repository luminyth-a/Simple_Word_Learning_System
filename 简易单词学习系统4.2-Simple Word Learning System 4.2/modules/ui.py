# ============================================================
# 文件: modules/ui.py
# 说明: 主界面UI模块 - 安全加固版
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import random
import json
import os
import csv
import sys
import re
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
        self.root.title(self.lang.get_text("app_title", "智能单词学习系统"))
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
        """保存易错词"""
        try:
            with open(self.wrong_words_file, 'w', encoding='utf-8') as f:
                json.dump(self.wrong_words, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存易错词失败: {e}")
    
    def add_to_wrong_words(self):
        """将当前单词添加到易错词表"""
        if not self.vocabulary:
            messagebox.showinfo(
                self.lang.get_text("tips", "提示"), 
                self.lang.get_text("no_word_learning", "没有正在学习的单词")
            )
            return
        
        current_word = self.vocabulary[self.current_index]
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
        
        self.wrong_words.append({
            'english': current_word['english'],
            'phonetic': phonetic,
            'pos_meaning': current_word.get('pos_meaning', ''),
            'usage': current_word.get('usage', ''),
            'root_affix': current_word.get('root_affix', ''),
            'tips': current_word.get('tips', ''),
            'collocations': current_word.get('collocations', ''),
            'synonyms': current_word.get('synonyms', ''),
            'antonyms': current_word.get('antonyms', ''),
            'examples': current_word.get('examples', ''),
            'wrong_count': 1,
            'add_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_wrong_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'is_phrase': False
        })
        self.save_wrong_words()
        messagebox.showinfo(
            self.lang.get_text("tips", "提示"), 
            f"「{current_word['english']}」{self.lang.get_text('added_to_wrong_word', '已添加到易错词表')}"
        )
    
    def _safe_error_message(self, error_msg):
        """
        安全显示错误信息（不泄露文件路径）
        修复漏洞8、9
        """
        error_str = str(error_msg)
        # 移除可能包含路径的信息
        # 只保留错误类型
        error_lines = error_str.strip().split('\n')
        safe_msgs = []
        for line in error_lines:
            # 过滤掉包含路径的行
            if '\\' not in line and '/' not in line:
                if line.strip():
                    safe_msgs.append(line.strip())
            else:
                # 提取错误类型
                if "Error:" in line or "Exception:" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        # 只取第一个部分作为错误类型
                        safe_msgs.append(parts[0].strip())
                else:
                    # 尝试提取文件名后的错误信息
                    parts = line.split("]")
                    if len(parts) >= 2:
                        safe_msgs.append(parts[-1].strip())
        
        if not safe_msgs:
            safe_msgs = ["操作失败，请重试"]
        
        return "\n".join(safe_msgs)[:500]  # 限制长度
    
    def _safe_csv_field(self, value):
        """
        CSV导出安全防护 - 防止公式注入
        修复漏洞3
        """
        if not value:
            return ""
        value = str(value)
        # 如果以 = + - @ 开头，添加单引号防止公式注入
        if value.startswith(('=', '+', '-', '@')):
            return "'" + value
        # 限制长度防止超长
        if len(value) > 2000:
            value = value[:2000] + "..."
        return value
    
    def export_wrong_words_to_csv(self):
        """导出易错词为CSV文件（安全版）"""
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
                    "词性.基本解释",
                    "用法说明",
                    "词根词缀",
                    "小贴士",
                    "常用搭配",
                    "近义词",
                    "反义词",
                    "例句",
                    self.lang.get_text("wrong_count", "错误次数")
                ])
                
                for word in sorted(self.wrong_words, key=lambda x: x.get('wrong_count', 0), reverse=True):
                    writer.writerow([
                        self._safe_csv_field(word.get('english', '')),
                        self._safe_csv_field(word.get('phonetic', '')),
                        self._safe_csv_field(word.get('pos_meaning', '')),
                        self._safe_csv_field(word.get('usage', '')),
                        self._safe_csv_field(word.get('root_affix', '')),
                        self._safe_csv_field(word.get('tips', '')),
                        self._safe_csv_field(word.get('collocations', '')),
                        self._safe_csv_field(word.get('synonyms', '')),
                        self._safe_csv_field(word.get('antonyms', '')),
                        self._safe_csv_field(word.get('examples', '')),
                        self._safe_csv_field(word.get('wrong_count', 0))
                    ])
            
            messagebox.showinfo(
                self.lang.get_text("export_success_title", "导出成功"), 
                self.lang.get_text("export_success", "易错词已导出到：\n{}").format(file_path)
            )
        except Exception as e:
            safe_msg = self._safe_error_message(e)
            messagebox.showerror(
                self.lang.get_text("export_failed_title", "导出失败"), 
                self.lang.get_text("export_failed", "导出时发生错误：\n{}").format(safe_msg)
            )
    
    def export_wrong_words_to_json(self):
        """导出易错词为JSON文件"""
        if not self.wrong_words:
            messagebox.showinfo(
                self.lang.get_text("tips", "提示"), 
                self.lang.get_text("no_wrong_words", "暂无易错词可导出")
            )
            return
        
        file_path = filedialog.asksaveasfilename(
            title=self.lang.get_text("export_json_title", "导出易错词为JSON"),
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialfile=f"wrong_words_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if not file_path:
            return
        
        try:
            export_data = []
            for word in sorted(self.wrong_words, key=lambda x: x.get('wrong_count', 0), reverse=True):
                pos_meaning_list = self.parse_pos_meanings_to_json(word.get('pos_meaning', ''))
                collocations_list = self.parse_list_to_json(word.get('collocations', ''), 'phrase', 'meaning')
                synonyms_list = self.parse_list_to_json(word.get('synonyms', ''), 'word', 'meaning')
                antonyms_list = self.parse_list_to_json(word.get('antonyms', ''), 'word', 'meaning')
                examples_list = self.parse_examples_to_json(word.get('examples', ''))
                
                export_data.append({
                    "english": word.get('english', ''),
                    "phonetic": word.get('phonetic', ''),
                    "pos_meaning": pos_meaning_list,
                    "usage": word.get('usage', ''),
                    "root_affix": word.get('root_affix', ''),
                    "tips": word.get('tips', ''),
                    "collocations": collocations_list,
                    "synonyms": synonyms_list,
                    "antonyms": antonyms_list,
                    "examples": examples_list
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo(
                self.lang.get_text("export_success_title", "导出成功"), 
                self.lang.get_text("export_success", "易错词已导出到：\n{}").format(file_path)
            )
        except Exception as e:
            safe_msg = self._safe_error_message(e)
            messagebox.showerror(
                self.lang.get_text("export_failed_title", "导出失败"), 
                self.lang.get_text("export_failed", "导出时发生错误：\n{}").format(safe_msg)
            )
    
    def parse_pos_meanings_to_json(self, pos_meaning_str):
        """将 pos_meaning 字符串解析为JSON数组格式"""
        result = []
        if not pos_meaning_str:
            return result
        
        parts = pos_meaning_str.split('|')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            match = re.match(r'^[【\[](.+?)[】\]](.+)$', part)
            if match:
                pos = match.group(1).strip()
                rest = match.group(2).strip()
                
                core = rest
                derived = ""
                
                core_match = re.search(r'（核心）(.+?)(（衍生）|$)', rest)
                if core_match:
                    core = core_match.group(1).strip()
                
                derived_match = re.search(r'（衍生）(.+?)$', rest)
                if derived_match:
                    derived = derived_match.group(1).strip()
                
                result.append({
                    "pos": pos,
                    "core": core,
                    "derived": derived
                })
            else:
                result.append({
                    "pos": "",
                    "core": part,
                    "derived": ""
                })
        
        return result
    
    def parse_list_to_json(self, text_str, key1, key2):
        """将分号分隔的列表解析为JSON数组格式"""
        result = []
        if not text_str:
            return result
        
        parts = re.split('[；]', text_str)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            match = re.match(r'^(.+?)（(.+?)）$', part)
            if match:
                result.append({
                    key1: match.group(1).strip(),
                    key2: match.group(2).strip()
                })
            else:
                result.append({
                    key1: part,
                    key2: ""
                })
        
        return result
    
    def parse_examples_to_json(self, examples_str):
        """将例句字符串解析为JSON数组格式"""
        result = []
        if not examples_str:
            return result
        
        parts = re.split('[；]', examples_str)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            match = re.match(r'^(.+?)（(.+?)）$', part)
            if match:
                result.append({
                    "en": match.group(1).strip(),
                    "cn": match.group(2).strip()
                })
            else:
                result.append({
                    "en": part,
                    "cn": ""
                })
        
        return result
    
    def view_wrong_words(self):
        """查看易错词表"""
        if not self.wrong_words:
            messagebox.showinfo(
                self.lang.get_text("wrong_words_title", "易错词表"), 
                self.lang.get_text("no_wrong_words_record", "暂无易错词记录")
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
        
        main_paned = ttk.PanedWindow(wrong_window, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ttk.Frame(main_paned)
        main_paned.add(tree_frame, weight=3)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = (
            self.lang.get_text("word", "单词"), 
            self.lang.get_text("phonetic", "音标"), 
            "词性", 
            self.lang.get_text("wrong_count", "错误次数"), 
            self.lang.get_text("add_time", "添加时间")
        )
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=150 if i < 4 else 140)
        
        for word in sorted(self.wrong_words, key=lambda x: x.get('wrong_count', 0), reverse=True):
            pos_text = word.get('pos_meaning', '').split('|')[0] if word.get('pos_meaning') else ''
            match = re.match(r'^[【\[](.+?)[】\]]', pos_text)
            if match:
                pos_text = match.group(1)
            tree.insert("", "end", values=(
                word.get('english', ''),
                word.get('phonetic', ''),
                pos_text[:30] + "..." if len(pos_text) > 30 else pos_text,
                word.get('wrong_count', 0),
                word.get('add_time', '')
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
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
                        # 使用语言文件
                        pos_title = self.lang.get_text("pos_title", "📌 词性与基本解释")
                        usage_title = self.lang.get_text("usage_title", "📖 用法说明")
                        root_title = self.lang.get_text("root_title", "🌱 词根词缀")
                        tips_title = self.lang.get_text("tips_title", "💡 小贴士")
                        examples_title = self.lang.get_text("examples_title", "📝 例句")
                        none_text = self.lang.get_text("none", "无")
                        
                        detail_text.insert(tk.END, f"【{pos_title}】\n{word.get('pos_meaning', none_text)}\n\n")
                        detail_text.insert(tk.END, f"【{usage_title}】\n{word.get('usage', none_text)}\n\n")
                        detail_text.insert(tk.END, f"【{root_title}】\n{word.get('root_affix', none_text)}\n\n")
                        detail_text.insert(tk.END, f"【{tips_title}】\n{word.get('tips', none_text)}\n\n")
                        detail_text.insert(tk.END, f"【{examples_title}】\n{word.get('examples', none_text)}")
                        break
        
        tree.bind('<<TreeviewSelect>>', on_tree_select)
        
        btn_frame = ttk.Frame(wrong_window)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text=self.lang.get_text("export_csv", "📁 导出CSV"), 
                  command=self.export_wrong_words_to_csv).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text=self.lang.get_text("export_json", "📁 导出JSON"), 
                  command=self.export_wrong_words_to_json).pack(side=tk.LEFT, padx=5)
        
        def clear_wrong_words():
            if messagebox.askyesno(self.lang.get_text("confirm", "确认"), 
                                   self.lang.get_text("confirm_clear", "确定要清空所有易错词记录吗？")):
                self.wrong_words = []
                self.save_wrong_words()
                wrong_window.destroy()
                messagebox.showinfo(self.lang.get_text("tips", "提示"), self.lang.get_text("cleared", "易错词表已清空"))
        
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
        
        self.title_var = tk.StringVar()
        self.title_var.set(self.lang.get_text("app_title", "智能单词学习系统"))
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
        self.root.title(self.lang.get_text("app_title", "智能单词学习系统"))
        self.title_var.set(self.lang.get_text("app_title", "智能单词学习系统"))
        
        self.phonetic_toggle_btn.config(text=self.lang.get_text("phonetic_on" if self.show_phonetic else "phonetic_off", 
                                                                "🔊 音标:开" if self.show_phonetic else "🔇 音标:关"))
        self.theme_btn.config(text=self.lang.get_text("dark_mode" if self.theme_mode == "light" else "light_mode", 
                                                      "🌙 暗色模式" if self.theme_mode == "light" else "☀️ 亮色模式"))
        self.view_wrong_btn.config(text=self.lang.get_text("wrong_words_list", "📋 易错词表"))
        
        if hasattr(self, 'lang_label'):
            self.lang_label.config(text=self.lang.get_text("language", "🌐 语言:"))
        
        self.refresh_mode_selector()
        self.refresh_control_buttons()
        
        self.quiz_label.config(text=self.lang.get_text("quiz_label", "请输入英文单词:"))
        self.check_btn.config(text=self.lang.get_text("check_answer", "✅ 检查答案"))
        
        self.refresh_language_menu()
        
        if self.vocabulary:
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
        
        # 仅保留 JSON 导入
        ttk.Button(file_frame, text=self.lang.get_text("import_json", "📁 导入JSON"), 
                  command=self.import_json).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text=self.lang.get_text("shuffle", "🔄 随机打乱"), 
                  command=self.shuffle_words).pack(side=tk.LEFT, padx=5)
        
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
    
    def parse_pos_meanings(self, pos_meaning_str):
        """
        解析词性.基本解释，支持多种格式
        
        格式1: "【代词】（核心）它；这；那（衍生）作形式主语/宾语"
        格式2: "[代词](核心)它；这；那(衍生)作形式主语/宾语"
        格式3: "【代词】（核心）它；这；那（衍生）作形式主语/宾语|【连词】（核心）引导从句"
        格式4: "代词.它；这；那"（兼容旧格式）
        
        输出: [{"pos": "代词", "meanings": ["（核心）它；这；那（衍生）作形式主语/宾语"]}, ...]
        """
        result = []
        if not pos_meaning_str:
            return result
        
        parts = pos_meaning_str.split('|')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            pos = ""
            meanings = []
            
            match = re.match(r'^【(.+?)】(.+)$', part)
            if match:
                pos = match.group(1).strip()
                rest = match.group(2).strip()
                meaning_list = re.split('[；;，,]', rest)
                meanings = [m.strip() for m in meaning_list if m.strip()]
                if meanings:
                    result.append({'pos': pos, 'meanings': meanings})
                continue
            
            match = re.match(r'^\[(.+?)\](.+)$', part)
            if match:
                pos = match.group(1).strip()
                rest = match.group(2).strip()
                meaning_list = re.split('[；;，,]', rest)
                meanings = [m.strip() for m in meaning_list if m.strip()]
                if meanings:
                    result.append({'pos': pos, 'meanings': meanings})
                continue
            
            if '.' in part:
                pos = part[:part.index('.')].strip()
                meanings_str = part[part.index('.') + 1:].strip()
                meanings = [m.strip() for m in re.split('[；;，,]', meanings_str) if m.strip()]
                if meanings:
                    result.append({'pos': pos, 'meanings': meanings})
                continue
            
            meanings = [m.strip() for m in re.split('[；;，,]', part) if m.strip()]
            if meanings:
                result.append({'pos': '', 'meanings': meanings})
        
        return result
    
    def create_word_card(self):
        """创建单词卡片（支持鼠标滚轮滚动）"""
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
        
        # ===== 绑定鼠标滚轮事件 =====
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _on_mousewheel_linux(event):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        
        def _bind_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self.canvas.bind_all("<Button-4>", _on_mousewheel_linux)
            self.canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        
        def _unbind_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        
        self.canvas.bind("<Enter>", _bind_mousewheel)
        self.canvas.bind("<Leave>", _unbind_mousewheel)
        
        self.content_frame = ttk.Frame(self.scrollable_frame)
        self.content_frame.pack(expand=True, fill=tk.BOTH, pady=10)
        
        # ===== 顶部：单词 + 音标 + 发音按钮 =====
        self.word_label = ttk.Label(self.content_frame, text="", 
                                   font=("Arial", 28, "bold"), foreground="#2c3e50", 
                                   wraplength=800, justify="center")
        self.word_label.pack(pady=(5, 3))
        
        self.phonetic_label = ttk.Label(self.content_frame, text="", 
                                       font=("Lucida Sans Unicode", 13, "italic"), foreground="#7f8c8d")
        self.phonetic_label.pack(pady=3)
        
        self.speak_btn = ttk.Button(self.content_frame, text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), 
                                   command=self.speak_current, width=16)
        self.speak_btn.pack(pady=5)
        
        self.sep1 = ttk.Separator(self.content_frame, orient='horizontal')
        self.sep1.pack(fill=tk.X, pady=8, padx=40)
        
        # ===== 1. 词性与基本解释 =====
        self.pos_frame = tk.Frame(self.content_frame, bg="#E8F0FE", relief="solid", bd=1)
        self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
        self.pos_label = tk.Label(self.pos_frame, text="", 
                                 font=("微软雅黑", 10), 
                                 fg="#1a237e",
                                 bg="#E8F0FE",
                                 wraplength=750,
                                 justify=tk.LEFT,
                                 padx=12,
                                 pady=8)
        self.pos_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== 2. 用法说明 =====
        self.usage_frame = tk.Frame(self.content_frame, bg="#FFF3E0", relief="solid", bd=1)
        self.usage_frame.pack(pady=5, fill=tk.X, padx=40)
        self.usage_label = tk.Label(self.usage_frame, text="", 
                                   font=("微软雅黑", 10), 
                                   fg="#BF360C",
                                   bg="#FFF3E0",
                                   wraplength=750,
                                   justify=tk.LEFT,
                                   padx=12,
                                   pady=8)
        self.usage_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== 3. 词根词缀 =====
        self.root_frame = tk.Frame(self.content_frame, bg="#F3E5F5", relief="solid", bd=1)
        self.root_frame.pack(pady=5, fill=tk.X, padx=40)
        self.root_label = tk.Label(self.root_frame, text="", 
                                  font=("微软雅黑", 10), 
                                  fg="#4A148C",
                                  bg="#F3E5F5",
                                  wraplength=750,
                                  justify=tk.LEFT,
                                  padx=12,
                                  pady=8)
        self.root_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== 4. 小贴士 =====
        self.tips_frame = tk.Frame(self.content_frame, bg="#FFF8E1", relief="solid", bd=1)
        self.tips_frame.pack(pady=5, fill=tk.X, padx=40)
        self.tips_label = tk.Label(self.tips_frame, text="", 
                                  font=("微软雅黑", 10), 
                                  fg="#E65100",
                                  bg="#FFF8E1",
                                  wraplength=750,
                                  justify=tk.LEFT,
                                  padx=12,
                                  pady=8)
        self.tips_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== 5. 常用搭配 =====
        self.collocation_frame = tk.Frame(self.content_frame, bg="#E0F7FA", relief="solid", bd=1)
        self.collocation_frame.pack(pady=5, fill=tk.X, padx=40)
        self.collocation_label = tk.Label(self.collocation_frame, text="", 
                                         font=("微软雅黑", 10), 
                                         fg="#006064",
                                         bg="#E0F7FA",
                                         wraplength=750,
                                         justify=tk.LEFT,
                                         padx=12,
                                         pady=8)
        self.collocation_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== 6. 近义词 + 反义词 =====
        self.syn_ant_frame = tk.Frame(self.content_frame, bg="#FCE4EC", relief="solid", bd=1)
        self.syn_ant_frame.pack(pady=5, fill=tk.X, padx=40)
        self.syn_ant_label = tk.Label(self.syn_ant_frame, text="", 
                                     font=("微软雅黑", 10), 
                                     fg="#880E4F",
                                     bg="#FCE4EC",
                                     wraplength=750,
                                     justify=tk.LEFT,
                                     padx=12,
                                     pady=8)
        self.syn_ant_label.pack(fill=tk.BOTH, expand=True)
        
        # ===== 7. 例句 =====
        self.example_frame = tk.Frame(self.content_frame, bg="#E8F5E9", relief="solid", bd=1)
        self.example_frame.pack(pady=5, fill=tk.X, padx=40)
        self.example_label = tk.Label(self.example_frame, text="", 
                                     font=("微软雅黑", 10), 
                                     fg="#1B5E20",
                                     bg="#E8F5E9",
                                     wraplength=750,
                                     justify=tk.LEFT,
                                     padx=12,
                                     pady=8)
        self.example_label.pack(fill=tk.BOTH, expand=True)
        
        self.hide_all_detail_frames()
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        if not self.tts.available:
            self.speak_btn.config(state="disabled", text="🔇 语音不可用")
    
    def _on_canvas_configure(self, event):
        """Canvas大小变化时更新内容宽度"""
        self.canvas.itemconfig(1, width=event.width - 20)
    
    def hide_all_detail_frames(self):
        """隐藏所有详情区域"""
        self.pos_frame.pack_forget()
        self.usage_frame.pack_forget()
        self.root_frame.pack_forget()
        self.tips_frame.pack_forget()
        self.collocation_frame.pack_forget()
        self.syn_ant_frame.pack_forget()
        self.example_frame.pack_forget()
        self.sep1.pack_forget()
    
    def create_quiz_panel(self):
        """创建默写/答题面板"""
        self.quiz_frame = ttk.Frame(self.main_frame)
        self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
        
        input_frame = ttk.Frame(self.quiz_frame)
        input_frame.pack(fill=tk.X, pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        self.quiz_label = ttk.Label(input_frame, text=self.lang.get_text("quiz_label", "请输入英文单词:"), 
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
        
        self.status_label = ttk.Label(status_frame, text=self.lang.get_text("status_welcome", "👋 欢迎使用智能单词学习系统"), 
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
        """播放当前单词发音"""
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
    
    def import_json(self):
        """导入JSON文件（安全版）"""
        file_path = filedialog.askopenfilename(
            title=self.lang.get_text("import_json_title", "选择JSON单词文件"),
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")])
        
        if not file_path:
            return
        
        try:
            self.vocabulary = CSVReader.read_json(file_path)
            self.current_index = 0
            self.switch_mode("study")
            self.update_display()
            count = len(self.vocabulary)
            self.status_label.config(text=self.lang.get_text("import_success", "✅ 成功导入 {} 个单词").format(count))
        except Exception as e:
            safe_msg = self._safe_error_message(e)
            messagebox.showerror(
                self.lang.get_text("import_error", "导入错误"), 
                f"{self.lang.get_text('import_failed', '导入失败')}：\n{safe_msg}"
            )
    
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
    
    def show_welcome(self):
        """显示欢迎界面"""
        self.word_label.config(text=self.lang.get_text("welcome_title", "📚 欢迎使用智能单词学习系统"), foreground="#2c3e50")
        self.phonetic_label.config(text="")
        self.speak_btn.config(state="disabled")
        
        self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
        self.pos_label.config(
            text=self.lang.get_text("tip_text", "💡 提示：\n\n• 点击【导入JSON】加载学习文件\n• 支持词性、用法、词根、搭配、近反义词等\n• 点击【忘了这个】可记录易错词"),
            fg="#2c3e50",
            bg="#ECF0F1",
            font=("微软雅黑", 10),
            justify=tk.LEFT
        )
        
        self.usage_frame.pack_forget()
        self.root_frame.pack_forget()
        self.tips_frame.pack_forget()
        self.collocation_frame.pack_forget()
        self.syn_ant_frame.pack_forget()
        self.example_frame.pack_forget()
        self.sep1.pack_forget()
        
        self.progress['value'] = 0
        self.count_label.config(text="0/0")
    
    def update_display(self):
        """根据当前模式更新显示"""
        if not self.vocabulary:
            self.show_welcome()
            return
        
        word = self.vocabulary[self.current_index]
        self.speak_btn.config(command=self.speak_current, state="normal")
        
        self.hide_all_detail_frames()
        
        if self.mode == "study":
            # ===== 学习模式：完整卡片 =====
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            phonetic_text = word['phonetic'] if self.show_phonetic else ""
            self.phonetic_label.config(text=phonetic_text)
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"))
            
            self.sep1.pack(fill=tk.X, pady=8, padx=40)
            
            # 1. 词性与基本解释
            if word.get('pos_meaning'):
                self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
                pos_data = self.parse_pos_meanings(word['pos_meaning'])
                title = self.lang.get_text("pos_title", "📌 词性与基本解释")
                display_text = title + "\n"
                for item in pos_data:
                    pos = item.get('pos', '')
                    meanings = '；'.join(item.get('meanings', []))
                    if pos:
                        display_text += f"  【{pos}】{meanings}\n"
                    else:
                        display_text += f"  {meanings}\n"
                self.pos_label.config(text=display_text.rstrip('\n'), fg="#1a237e", bg="#E8F0FE")
                self.pos_frame.config(bg="#E8F0FE")
            else:
                self.pos_frame.pack_forget()
            
            # 2. 用法说明
            if word.get('usage'):
                self.usage_frame.pack(pady=5, fill=tk.X, padx=40)
                title = self.lang.get_text("usage_title", "📖 用法说明")
                self.usage_label.config(text=f"{title}\n{word['usage']}", fg="#BF360C", bg="#FFF3E0")
                self.usage_frame.config(bg="#FFF3E0")
            else:
                self.usage_frame.pack_forget()
            
            # 3. 词根词缀
            if word.get('root_affix'):
                self.root_frame.pack(pady=5, fill=tk.X, padx=40)
                title = self.lang.get_text("root_title", "🌱 词根词缀")
                self.root_label.config(text=f"{title}\n{word['root_affix']}", fg="#4A148C", bg="#F3E5F5")
                self.root_frame.config(bg="#F3E5F5")
            else:
                self.root_frame.pack_forget()
            
            # 4. 小贴士
            if word.get('tips'):
                self.tips_frame.pack(pady=5, fill=tk.X, padx=40)
                title = self.lang.get_text("tips_title", "💡 小贴士")
                self.tips_label.config(text=f"{title}\n{word['tips']}", fg="#E65100", bg="#FFF8E1")
                self.tips_frame.config(bg="#FFF8E1")
            else:
                self.tips_frame.pack_forget()
            
            # 5. 常用搭配
            self.collocation_frame.pack(pady=5, fill=tk.X, padx=40)
            coll_text = word.get('collocations', '')
            title = self.lang.get_text("collocations_title", "🔗 常用搭配")
            if coll_text:
                parts = re.split('[；]', coll_text)
                formatted = []
                for p in parts:
                    p = p.strip()
                    if p:
                        p = p.replace('；', '，')
                        formatted.append(p)
                display = title + "\n" + '  |  '.join(formatted)
            else:
                display = title + "\n" + self.lang.get_text("no_collocations", "无常用搭配")
            self.collocation_label.config(text=display, fg="#006064", bg="#E0F7FA")
            self.collocation_frame.config(bg="#E0F7FA")
            
            # 6. 近义词 + 反义词
            syn_text = word.get('synonyms', '')
            ant_text = word.get('antonyms', '')
            
            self.syn_ant_frame.pack(pady=5, fill=tk.X, padx=40)
            syn_title = self.lang.get_text("synonyms_title", "📊 近义词")
            ant_title = self.lang.get_text("antonyms_title", "🔄 反义词")
            
            display = syn_title + "  "
            if syn_text:
                parts = re.split('[；]', syn_text)
                formatted = []
                for p in parts:
                    p = p.strip()
                    if p:
                        p = p.replace('；', '，')
                        formatted.append(p)
                display += "  |  ".join(formatted)
            else:
                display += self.lang.get_text("no_synonyms", "无近义词")
            
            display += "\n" + ant_title + "  "
            if ant_text:
                parts = re.split('[；]', ant_text)
                formatted = []
                for p in parts:
                    p = p.strip()
                    if p:
                        p = p.replace('；', '，')
                        formatted.append(p)
                display += "  |  ".join(formatted)
            else:
                display += self.lang.get_text("no_antonyms", "无反义词")
            
            self.syn_ant_label.config(text=display, fg="#880E4F", bg="#FCE4EC")
            self.syn_ant_frame.config(bg="#FCE4EC")
            
            # 7. 例句
            if word.get('examples'):
                self.example_frame.pack(pady=5, fill=tk.X, padx=40)
                examples_text = word['examples']
                parts = re.split('[；;]', examples_text)
                formatted = []
                for p in parts:
                    p = p.strip()
                    if p:
                        match = re.match(r'^(.+?)（(.+?)）$', p)
                        if match:
                            en = match.group(1).strip()
                            cn = match.group(2).strip()
                            formatted.append(f"• {en}")
                            formatted.append(f"  {cn}")
                        else:
                            formatted.append(f"• {p}")
                title = self.lang.get_text("examples_title", "📝 例句")
                display = title + "\n" + '\n'.join(formatted)
                self.example_label.config(text=display, fg="#1B5E20", bg="#E8F5E9")
                self.example_frame.config(bg="#E8F5E9")
            else:
                self.example_frame.pack_forget()
        
        elif self.mode == "listen":
            # ===== 听力模式：??? + 发音按钮 =====
            self.word_label.config(text="🎧 ???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.speak_btn.config(text=self.lang.get_text("listen_and_guess", "🎧 播放发音并猜词"), command=self.listen_and_guess)
            
            self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
            hint_title = self.lang.get_text("listen_hint_title", "📌 提示")
            hint_text = self.lang.get_text("listen_hint_text", "点击下方按钮听发音，然后在对话框中输入单词")
            length_text = self.lang.get_text("listen_length", "单词长度")
            self.pos_label.config(
                text=f"{hint_title}\n{length_text}: {len(word['english'])} 个字符\n\n{hint_text}",
                fg="#1a237e",
                bg="#E8F0FE"
            )
            self.pos_frame.config(bg="#E8F0FE")
        
        elif self.mode == "speak":
            # ===== 口语模式：??? + 发音按钮 + 词性（不显示用法） =====
            self.word_label.config(text="???", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.speak_btn.config(text=self.lang.get_text("play_standard", "🔊 播放标准发音"), command=self.speak_current)
            
            # 只显示词性与基本解释，不显示用法说明
            if word.get('pos_meaning'):
                self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
                pos_data = self.parse_pos_meanings(word['pos_meaning'])
                title = self.lang.get_text("pos_title", "📌 词性与基本解释")
                display_text = title + "\n"
                for item in pos_data:
                    pos = item.get('pos', '')
                    meanings = '；'.join(item.get('meanings', []))
                    if pos:
                        display_text += f"  【{pos}】{meanings}\n"
                    else:
                        display_text += f"  {meanings}\n"
                self.pos_label.config(text=display_text.rstrip('\n'), fg="#1a237e", bg="#E8F0FE")
                self.pos_frame.config(bg="#E8F0FE")
            else:
                self.pos_frame.pack_forget()
            
            # 用法说明不显示
            
            # 提示信息
            self.tips_frame.pack(pady=5, fill=tk.X, padx=40)
            speak_hint = self.lang.get_text("speak_hint_text", "请说出对应的英文单词，然后点击播放发音对照")
            self.tips_label.config(
                text=f"💡 {speak_hint}",
                fg="#E65100",
                bg="#FFF8E1"
            )
            self.tips_frame.config(bg="#FFF8E1")
        
        elif self.mode == "read":
            # ===== 阅读模式：英文 + 音标 + 发音 =====
            self.word_label.config(text=word['english'], foreground="#2c3e50")
            phonetic_text = word['phonetic'] if self.show_phonetic else ""
            self.phonetic_label.config(text=phonetic_text)
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 播放发音"), command=self.speak_current)
            
            self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
            question = self.lang.get_text("read_question", "❓ 这个单词是什么意思？")
            hint1 = self.lang.get_text("read_hint1", "理解这个单词的意思，然后点击发音确认")
            hint2 = self.lang.get_text("read_hint2", "提示：点击「下一个」查看下一个单词")
            self.pos_label.config(
                text=f"{question}\n\n{hint1}\n\n{hint2}",
                fg="#1a237e",
                bg="#E8F0FE"
            )
            self.pos_frame.config(bg="#E8F0FE")
        
        elif self.mode == "write":
            # ===== 默写模式：标题 + 发音 + 词性（不显示用法） + 输入框 =====
            write_title = self.lang.get_text("write_title", "✏️ 请默写英文单词")
            self.word_label.config(text=write_title, foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.speak_btn.config(text=self.lang.get_text("play_pronunciation", "🔊 听发音提示"), command=self.speak_current)
            
            # 只显示词性与基本解释，不显示用法说明
            if word.get('pos_meaning'):
                self.pos_frame.pack(pady=5, fill=tk.X, padx=40)
                pos_data = self.parse_pos_meanings(word['pos_meaning'])
                title = self.lang.get_text("pos_title", "📌 词性与基本解释")
                display_text = title + "\n"
                for item in pos_data:
                    pos = item.get('pos', '')
                    meanings = '；'.join(item.get('meanings', []))
                    if pos:
                        display_text += f"  【{pos}】{meanings}\n"
                    else:
                        display_text += f"  {meanings}\n"
                self.pos_label.config(text=display_text.rstrip('\n'), fg="#1a237e", bg="#E8F0FE")
                self.pos_frame.config(bg="#E8F0FE")
            else:
                self.pos_frame.pack_forget()
            
            # 用法说明不显示
            
            self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
            self.quiz_label.config(text=self.lang.get_text("quiz_label", "请输入英文单词:"))
            self.quiz_entry.focus()
        
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
            self.lang.get_text("listen_question", "播放的单词是什么？\n提示: {} 个字符").format(len(word['english'])),
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
            self.pos_label.config(bg="#1a237e", fg="#BBDEFB")
            self.pos_frame.config(bg="#1a237e")
            self.usage_label.config(bg="#BF360C", fg="#FFCCBC")
            self.usage_frame.config(bg="#BF360C")
            self.root_label.config(bg="#4A148C", fg="#E1BEE7")
            self.root_frame.config(bg="#4A148C")
            self.tips_label.config(bg="#E65100", fg="#FFE0B2")
            self.tips_frame.config(bg="#E65100")
            self.collocation_label.config(bg="#006064", fg="#B2EBF2")
            self.collocation_frame.config(bg="#006064")
            self.syn_ant_label.config(bg="#880E4F", fg="#F8BBD0")
            self.syn_ant_frame.config(bg="#880E4F")
            self.example_label.config(bg="#1B5E20", fg="#C8E6C9")
            self.example_frame.config(bg="#1B5E20")
        else:
            self.theme_mode = "light"
            self.theme_btn.config(text=self.lang.get_text("dark_mode", "🌙 暗色模式"))
            self.root.configure(bg="#f5f5f5")
            self.status_label.config(foreground="#7f8c8d")
            self.pos_label.config(bg="#E8F0FE", fg="#1a237e")
            self.pos_frame.config(bg="#E8F0FE")
            self.usage_label.config(bg="#FFF3E0", fg="#BF360C")
            self.usage_frame.config(bg="#FFF3E0")
            self.root_label.config(bg="#F3E5F5", fg="#4A148C")
            self.root_frame.config(bg="#F3E5F5")
            self.tips_label.config(bg="#FFF8E1", fg="#E65100")
            self.tips_frame.config(bg="#FFF8E1")
            self.collocation_label.config(bg="#E0F7FA", fg="#006064")
            self.collocation_frame.config(bg="#E0F7FA")
            self.syn_ant_label.config(bg="#FCE4EC", fg="#880E4F")
            self.syn_ant_frame.config(bg="#FCE4EC")
            self.example_label.config(bg="#E8F5E9", fg="#1B5E20")
            self.example_frame.config(bg="#E8F5E9")