import json
import os
import sys
import re

class LanguageManager:
    """语言管理器（安全版本）"""
    
    # 允许的语言文件白名单（修复漏洞4）
    ALLOWED_LANGUAGES = {
        'zh-CN', 'zh-TW', 'en-US', 'ja-JP', 'ko-KR',
        'es-ES', 'fr-FR', 'de-DE', 'ru-RU', 'ar-SA'
    }
    MAX_FILE_SIZE = 1024 * 1024  # 1MB 限制（修复漏洞4）
    
    def __init__(self):
        self.current_language = "zh-CN"
        self.languages = {}
        self.texts = {}
        self.config_file = "language_config.json"
        self.load_languages()
        self.load_saved_language()
    
    def get_language_folder(self):
        """获取语言文件夹路径"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_path, "Language")
    
    def load_languages(self):
        """加载所有可用的语言（安全版本）"""
        lang_folder = self.get_language_folder()
        
        if not os.path.exists(lang_folder):
            os.makedirs(lang_folder)
            self.create_default_languages(lang_folder)
        
        self.languages = {}
        for filename in os.listdir(lang_folder):
            if not filename.endswith('.json'):
                continue
            
            # 安全验证1：只允许白名单中的语言（修复漏洞4）
            lang_code = filename[:-5]  # 移除 .json
            if lang_code not in self.ALLOWED_LANGUAGES:
                print(f"跳过不允许的语言文件: {filename}")
                continue
            
            # 安全验证2：防止路径遍历（修复漏洞11）
            safe_filename = os.path.basename(filename)
            if safe_filename != filename:
                print(f"跳过非法文件名: {filename}")
                continue
            
            filepath = os.path.join(lang_folder, safe_filename)
            
            # 安全验证3：文件大小限制（修复漏洞4）
            try:
                file_size = os.path.getsize(filepath)
                if file_size > self.MAX_FILE_SIZE:
                    print(f"语言文件 {filename} 过大 ({file_size} bytes)，跳过加载")
                    continue
            except:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lang_data = json.load(f)
                    lang_code = lang_data.get('language_code', filename[:-5])
                    lang_name = lang_data.get('language_name', lang_code)
                    self.languages[lang_code] = {
                        'name': lang_name,
                        'file': filepath,
                        'data': lang_data
                    }
            except Exception as e:
                print(f"加载语言文件 {filename} 失败: {e}")
    
    def create_default_languages(self, lang_folder):
        """创建默认语言文件"""
        default_langs = {
            'zh-CN': {
                "language_name": "简体中文",
                "language_code": "zh-CN",
                "app_title": "智能单词学习系统",
                "study_mode": "📖 学习模式",
                "listen_mode": "👂 听力模式",
                "speak_mode": "🗣️ 口语模式",
                "read_mode": "📖 阅读模式",
                "write_mode": "✏️ 默写模式",
                "select_mode": "选择学习模式",
                "study_content": "学习内容",
                "phonetic_on": "🔊 音标:开",
                "phonetic_off": "🔇 音标:关",
                "dark_mode": "🌙 暗色模式",
                "light_mode": "☀️ 亮色模式",
                "language": "🌐 语言",
                "play_pronunciation": "🔊 播放发音",
                "play_standard": "🔊 播放标准发音",
                "listen_and_guess": "🎧 播放发音并猜词",
                "listen_hint": "🎧 点击按钮听发音，然后在对话框中输入单词",
                "speak_hint": "🗣️ 请说出对应的英文单词，然后点击播放发音对照",
                "read_hint": "📖 理解这个单词的意思，然后点击发音确认",
                "write_hint": "💡 根据上方中文意思默写英文单词",
                "quiz_label": "请输入英文单词:",
                "check_answer": "✅ 检查答案",
                "correct": "✅ 回答正确！",
                "wrong": "❌ 错误！正确答案: ",
                "please_input": "⚠️ 请输入答案",
                "import_csv": "📁 导入CSV",
                "import_csv_title": "选择CSV单词文件",
                "import_json": "📁 导入JSON",
                "import_json_title": "选择JSON单词文件",
                "export_json": "📁 导出JSON",
                "export_json_title": "导出易错词为JSON",
                "shuffle": "🔄 随机打乱",
                "forgot_word": "📌 忘了这个",
                "forgot_phrase": "📌 忘了这个",
                "wrong_words_list": "📋 易错词表",
                "wrong_words_title": "📋 易错词表",
                "no_wrong_words": "暂无易错词可导出",
                "no_wrong_words_record": "暂无易错词记录\n\n学习过程中点击「忘了这个」按钮即可记录",
                "wrong_words_stats": "共 {} 个易错词，累计错误 {} 次",
                "export_csv": "📁 导出CSV",
                "export_success_title": "导出成功",
                "export_success": "易错词已导出到：\n{}",
                "export_failed_title": "导出失败",
                "export_failed": "导出时发生错误：\n{}",
                "delete_selected": "🗑️ 删除选中",
                "clear_all": "🗑️ 清空全部",
                "close": "关闭",
                "confirm_clear": "确定要清空所有易错词记录吗？",
                "select_word_first": "请先选择要删除的单词",
                "previous": "⬅️ 上一个",
                "next": "下一个 ➡️",
                "listening_test": "听力测试",
                "listen_question": "播放的单词是什么？\n提示: {} 个字符",
                "correct_answer": "✅ 回答正确！",
                "wrong_answer": "❌ 回答错误！\n正确答案: {}\n你的答案: {}",
                "import_success": "✅ 成功导入 {} 个单词",
                "import_error": "导入错误",
                "import_failed": "导入失败",
                "load_success": "✅ 已加载 {} 个示例单词",
                "shuffle_success": "🔀 单词顺序已打乱",
                "playing": "🔊 正在播放: {}",
                "listening_played": "🔊 已播放，请猜词...",
                "answer_is": "答案: {}",
                "word_type": "单词",
                "phrase_type": "词组",
                "mode_study": "学习模式",
                "mode_listen": "听力模式",
                "mode_speak": "口语模式",
                "mode_read": "阅读模式",
                "mode_write": "默写模式",
                "mode_switched": "🎯 {} - 开始学习吧！",
                "status_welcome": "👋 欢迎使用智能单词学习系统",
                "example_sentence": "例句",
                "translation": "翻译",
                "word_breakdown": "单词拆解",
                "root_analysis": "词根分析",
                "detail_info": "详细信息",
                "word": "单词",
                "phonetic": "音标",
                "meaning": "意思",
                "morpheme": "语素/拆解",
                "wrong_count": "错误次数",
                "add_time": "添加时间",
                "confirm": "确认",
                "tips": "提示",
                "cleared": "易错词表已清空",
                "no_word_learning": "没有正在学习的单词",
                "wrong_count_updated": "错误次数已更新",
                "added_to_wrong_word": "已添加到易错词表",
                "added_to_wrong_phrase": "已添加到易错词表（复式）",
                "none": "无",
                "tip_text": "💡 提示：\n\n• 点击【导入JSON】加载学习文件\n• 支持词性、用法、词根、搭配、近反义词等\n• 点击【忘了这个】可记录易错词",
                "welcome_title": "📚 欢迎使用智能单词学习系统",
                "app_title": "智能单词学习系统",
                "language_name": "简体中文",
                "pos_title": "📌 词性与基本解释",
                "usage_title": "📖 用法说明",
                "root_title": "🌱 词根词缀",
                "tips_title": "💡 小贴士",
                "collocations_title": "🔗 常用搭配",
                "synonyms_title": "📊 近义词",
                "antonyms_title": "🔄 反义词",
                "examples_title": "📝 例句",
                "listen_hint_title": "📌 提示",
                "listen_hint_text": "点击下方按钮听发音，然后在对话框中输入单词",
                "listen_length": "单词长度",
                "speak_hint_text": "请说出对应的英文单词，然后点击播放发音对照",
                "read_question": "❓ 这个单词是什么意思？",
                "read_hint1": "理解这个单词的意思，然后点击发音确认",
                "read_hint2": "提示：点击「下一个」查看下一个单词",
                "write_title": "✏️ 请默写英文单词",
                "no_collocations": "无常用搭配",
                "no_synonyms": "无近义词",
                "no_antonyms": "无反义词"
            },
            'en-US': {
                "language_name": "English",
                "language_code": "en-US",
                "app_title": "Smart Vocabulary Learning System",
                "study_mode": "📖 Study Mode",
                "listen_mode": "👂 Listen Mode",
                "speak_mode": "🗣️ Speak Mode",
                "read_mode": "📖 Read Mode",
                "write_mode": "✏️ Write Mode",
                "select_mode": "Select Learning Mode",
                "study_content": "Learning Content",
                "phonetic_on": "🔊 Phonetic:On",
                "phonetic_off": "🔇 Phonetic:Off",
                "dark_mode": "🌙 Dark Mode",
                "light_mode": "☀️ Light Mode",
                "language": "🌐 Language",
                "play_pronunciation": "🔊 Play",
                "play_standard": "🔊 Standard Pronunciation",
                "listen_and_guess": "🎧 Listen & Guess",
                "listen_hint": "🎧 Click to listen, then enter the word",
                "speak_hint": "🗣️ Say the word, then click to compare",
                "read_hint": "📖 Understand the meaning, then click to listen",
                "write_hint": "💡 Write the English word based on the meaning",
                "quiz_label": "Enter the English word:",
                "check_answer": "✅ Check",
                "correct": "✅ Correct!",
                "wrong": "❌ Wrong! Correct answer: ",
                "please_input": "⚠️ Please enter an answer",
                "import_csv": "📁 Import CSV",
                "import_csv_title": "Select CSV Word File",
                "import_json": "📁 Import JSON",
                "import_json_title": "Select JSON Word File",
                "export_json": "📁 Export JSON",
                "export_json_title": "Export Wrong Words as JSON",
                "shuffle": "🔄 Shuffle",
                "forgot_word": "📌 Forgot",
                "forgot_phrase": "📌 Forgot",
                "wrong_words_list": "📋 Wrong Words",
                "wrong_words_title": "📋 Wrong Words List",
                "no_wrong_words": "No wrong words to export",
                "no_wrong_words_record": "No wrong words recorded yet.\n\nClick 'Forgot' during learning to record.",
                "wrong_words_stats": "Total {} word(s), {} error(s)",
                "export_csv": "📁 Export CSV",
                "export_success_title": "Export Successful",
                "export_success": "Wrong words exported to:\n{}",
                "export_failed_title": "Export Failed",
                "export_failed": "Export failed:\n{}",
                "delete_selected": "🗑️ Delete Selected",
                "clear_all": "🗑️ Clear All",
                "close": "Close",
                "confirm_clear": "Are you sure you want to clear all wrong word records?",
                "select_word_first": "Please select a word to delete first",
                "previous": "⬅️ Previous",
                "next": "Next ➡️",
                "listening_test": "Listening Test",
                "listen_question": "What word did you hear?\nHint: {} characters",
                "correct_answer": "✅ Correct!",
                "wrong_answer": "❌ Wrong!\nCorrect: {}\nYour answer: {}",
                "import_success": "✅ Successfully imported {} words",
                "import_error": "Import Error",
                "import_failed": "Import failed",
                "load_success": "✅ Loaded {} sample words",
                "shuffle_success": "🔀 Word order shuffled",
                "playing": "🔊 Playing: {}",
                "listening_played": "🔊 Played, guess the word...",
                "answer_is": "Answer: {}",
                "word_type": "word(s)",
                "phrase_type": "phrase(s)",
                "mode_study": "Study Mode",
                "mode_listen": "Listen Mode",
                "mode_speak": "Speak Mode",
                "mode_read": "Read Mode",
                "mode_write": "Write Mode",
                "mode_switched": "🎯 {} - Let's start learning!",
                "status_welcome": "👋 Welcome to Smart Vocabulary Learning System",
                "example_sentence": "Example",
                "translation": "Translation",
                "word_breakdown": "Breakdown",
                "root_analysis": "Root Analysis",
                "detail_info": "Details",
                "word": "Word",
                "phonetic": "Phonetic",
                "meaning": "Meaning",
                "morpheme": "Morpheme",
                "wrong_count": "Count",
                "add_time": "Added",
                "confirm": "Confirm",
                "tips": "Tips",
                "cleared": "Wrong word list cleared",
                "no_word_learning": "No word learning",
                "wrong_count_updated": "count updated",
                "added_to_wrong_word": "added to wrong list",
                "added_to_wrong_phrase": "added to wrong list (compound)",
                "none": "None",
                "tip_text": "💡 Tips:\n\n• Click 'Import JSON' to load your own learning files\n• Morpheme info displayed in prominent colors\n• Example sentences with translations\n• Click 'Forgot' to record difficult words",
                "welcome_title": "📚 Welcome to Smart Vocabulary Learning System",
                "language_name": "English",
                "pos_title": "📌 Part of Speech & Meaning",
                "usage_title": "📖 Usage",
                "root_title": "🌱 Root & Affix",
                "tips_title": "💡 Tips",
                "collocations_title": "🔗 Collocations",
                "synonyms_title": "📊 Synonyms",
                "antonyms_title": "🔄 Antonyms",
                "examples_title": "📝 Examples",
                "listen_hint_title": "📌 Hint",
                "listen_hint_text": "Click the button to listen, then enter the word in the dialog",
                "listen_length": "Word length",
                "speak_hint_text": "Say the English word, then click to compare pronunciation",
                "read_question": "❓ What does this word mean?",
                "read_hint1": "Understand the meaning, then click to listen",
                "read_hint2": "Hint: Click 'Next' to see the next word",
                "write_title": "✏️ Please write the English word",
                "no_collocations": "No collocations",
                "no_synonyms": "No synonyms",
                "no_antonyms": "No antonyms"
            }
        }
        
        for code, data in default_langs.items():
            filepath = os.path.join(lang_folder, f"{code}.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_saved_language(self):
        """加载保存的语言设置"""
        if getattr(sys, 'frozen', False):
            config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'VocabSystem')
        else:
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        os.makedirs(config_dir, exist_ok=True)
        self.config_file = os.path.join(config_dir, "language_config.json")
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_lang = config.get('language', 'zh-CN')
                    if saved_lang in self.languages:
                        self.current_language = saved_lang
            except:
                pass
        
        self.load_texts()
    
    def load_texts(self):
        """加载当前语言的文本"""
        if self.current_language in self.languages:
            self.texts = self.languages[self.current_language]['data']
        else:
            first_lang = list(self.languages.keys())[0] if self.languages else 'zh-CN'
            self.texts = self.languages.get(first_lang, {}).get('data', {})
    
    def save_language(self, lang_code):
        """保存语言设置"""
        if lang_code in self.languages:
            self.current_language = lang_code
            self.load_texts()
            
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump({'language': lang_code}, f, ensure_ascii=False, indent=2)
                return True
            except:
                return False
        return False
    
    def get_text(self, key, default=""):
        """获取翻译文本"""
        return self.texts.get(key, default)
    
    def get_language_list(self):
        """获取可用语言列表"""
        return [(code, info['name']) for code, info in self.languages.items()]
    
    def get_current_language(self):
        """获取当前语言"""
        return self.current_language