import json
import os
import sys

class LanguageManager:
    """语言管理器"""
    
    def __init__(self):
        self.current_language = "zh-CN"
        self.languages = {}
        self.texts = {}
        self.config_file = "language_config.json"
        self.load_languages()
        self.load_saved_language()
    
    def get_language_folder(self):
        """获取语言文件夹路径（支持打包后的路径）"""
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            base_path = sys._MEIPASS
        else:
            # 开发环境路径
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_path, "Language")
    
    def load_languages(self):
        """加载所有可用的语言"""
        lang_folder = self.get_language_folder()
        
        if not os.path.exists(lang_folder):
            os.makedirs(lang_folder)
            self.create_default_languages(lang_folder)
        
        self.languages = {}
        for filename in os.listdir(lang_folder):
            if filename.endswith('.json'):
                filepath = os.path.join(lang_folder, filename)
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
                "app_title": "智能单词学习系统 - 听说读写全能版"
            },
            'en-US': {
                "language_name": "English",
                "language_code": "en-US",
                "app_title": "Smart Vocabulary Learning System - All-in-One"
            }
        }
        
        for code, data in default_langs.items():
            filepath = os.path.join(lang_folder, f"{code}.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_saved_language(self):
        """加载保存的语言设置"""
        # 获取配置文件路径（保存到用户目录，避免权限问题）
        if getattr(sys, 'frozen', False):
            # 打包后保存到用户目录
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
            # 默认使用第一个可用语言
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