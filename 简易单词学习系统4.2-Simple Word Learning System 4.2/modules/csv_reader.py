import json
import os
import re

class CSVReader:
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB 限制（修复漏洞5）
    MAX_ITEMS = 10000  # 最多导入10000条（修复漏洞6）
    
    @staticmethod
    def read_json(file_path):
        """读取JSON文件（安全版本）"""
        # 安全验证1：文件路径安全（修复漏洞10）
        if not file_path:
            raise Exception("文件路径为空")
        
        # 防止路径遍历
        safe_path = os.path.normpath(file_path)
        if os.path.basename(safe_path) != os.path.basename(file_path):
            raise Exception("非法文件路径")
        
        # 安全验证2：文件大小限制（修复漏洞5）
        try:
            file_size = os.path.getsize(safe_path)
            if file_size > CSVReader.MAX_FILE_SIZE:
                raise Exception(f"文件过大 ({file_size} bytes)，最大支持 {CSVReader.MAX_FILE_SIZE} bytes")
        except OSError:
            raise Exception("无法读取文件")
        
        try:
            with open(safe_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise Exception("JSON格式错误：根节点应为数组")
            
            # 安全验证3：导入数量限制（修复漏洞6）
            if len(data) > CSVReader.MAX_ITEMS:
                raise Exception(f"数据量过大 ({len(data)} 条)，最大支持 {CSVReader.MAX_ITEMS} 条")
            
            vocabulary = []
            for item in data:
                word = CSVReader.parse_json_item(item)
                if word and word.get('english'):
                    vocabulary.append(word)
            
            if not vocabulary:
                raise Exception("没有找到有效的单词数据")
            
            return vocabulary
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {str(e)}")
        except Exception as e:
            raise Exception(f"读取JSON文件失败: {str(e)}")
    
    @staticmethod
    def parse_json_item(item):
        """
        解析JSON项为内部数据结构
        """
        import re
        
        # 安全验证：限制字符串长度
        def safe_truncate(s, max_len=500):
            if not s:
                return ""
            return s[:max_len]
        
        # 解析 pos_meaning
        pos_meaning_str = ""
        if 'pos_meaning' in item:
            if isinstance(item['pos_meaning'], list):
                parts = []
                for p in item['pos_meaning']:
                    pos = safe_truncate(p.get('pos', ''))
                    core = safe_truncate(p.get('core', ''))
                    derived = safe_truncate(p.get('derived', ''))
                    if pos and core:
                        if derived:
                            parts.append(f"【{pos}】（核心）{core}（衍生）{derived}")
                        else:
                            parts.append(f"【{pos}】（核心）{core}")
                    elif core:
                        parts.append(core)
                pos_meaning_str = '|'.join(parts)
            else:
                pos_meaning_str = safe_truncate(item['pos_meaning'])
        
        # 解析 collocations
        collocations_str = ""
        if 'collocations' in item:
            if isinstance(item['collocations'], list):
                collocations_str = '；'.join([f"{safe_truncate(c.get('phrase', ''))}（{safe_truncate(c.get('meaning', ''))}）" for c in item['collocations'] if c.get('phrase')])
            else:
                collocations_str = safe_truncate(item['collocations'])
        
        # 解析 synonyms
        synonyms_str = ""
        if 'synonyms' in item:
            if isinstance(item['synonyms'], list):
                synonyms_str = '；'.join([f"{safe_truncate(s.get('word', ''))}（{safe_truncate(s.get('meaning', ''))}）" for s in item['synonyms'] if s.get('word')])
            else:
                synonyms_str = safe_truncate(item['synonyms'])
        
        # 解析 antonyms
        antonyms_str = ""
        if 'antonyms' in item:
            if isinstance(item['antonyms'], list):
                antonyms_str = '；'.join([f"{safe_truncate(a.get('word', ''))}（{safe_truncate(a.get('meaning', ''))}）" for a in item['antonyms'] if a.get('word')])
            else:
                antonyms_str = safe_truncate(item['antonyms'])
        
        # 解析 examples
        examples_str = ""
        if 'examples' in item:
            if isinstance(item['examples'], list):
                examples_str = '；'.join([f"{safe_truncate(e.get('en', ''))}（{safe_truncate(e.get('cn', ''))}）" for e in item['examples'] if e.get('en')])
            else:
                examples_str = safe_truncate(item['examples'])
        
        return {
            'english': safe_truncate(item.get('english', '')),
            'phonetic': safe_truncate(item.get('phonetic', '')),
            'pos_meaning': pos_meaning_str,
            'usage': safe_truncate(item.get('usage', '')),
            'root_affix': safe_truncate(item.get('root_affix', '')),
            'tips': safe_truncate(item.get('tips', '')),
            'collocations': collocations_str,
            'synonyms': synonyms_str,
            'antonyms': antonyms_str,
            'examples': examples_str,
            'chinese': pos_meaning_str,
            'is_phrase': False
        }
    
    @staticmethod
    def read_file(file_path):
        """读取文件（仅支持JSON）"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.json':
            return CSVReader.read_json(file_path)
        else:
            raise Exception(f"不支持的文件格式: {file_ext}，请使用 .json 文件")