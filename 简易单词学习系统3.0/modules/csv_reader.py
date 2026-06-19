import csv
import re
import os

class CSVReader:
    @staticmethod
    def read_csv(file_path):
        """读取CSV文件，自动识别单词或词组"""
        vocabulary = []
        
        try:
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        content = content.replace('\ufeff', '')
                        lines = content.strip().split('\n')
                        
                        if not lines:
                            continue
                        
                        # 读取表头判断类型
                        header = lines[0].strip().lower()
                        
                        for line_num, line in enumerate(lines[1:], 2):
                            if not line.strip():
                                continue
                            
                            # 解析CSV行
                            parts = CSVReader.parse_csv_line(line)
                            
                            if len(parts) < 2:
                                continue
                            
                            # 判断是单词还是词组
                            if '词组' in header or '短语' in header or 'phrase' in header or '复式' in header:
                                item = CSVReader.process_phrase_format(parts)
                            else:
                                item = CSVReader.process_word_format(parts)
                            
                            if item and item.get('english'):
                                vocabulary.append(item)
                        
                        if vocabulary:
                            return vocabulary
                            
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"编码 {encoding} 读取失败: {str(e)}")
                    continue
            
            if not vocabulary:
                raise Exception("无法读取文件，请检查文件格式和编码")
                
        except Exception as e:
            raise Exception(f"读取CSV文件失败: {str(e)}")
    
    @staticmethod
    def parse_csv_line(line):
        """解析CSV行"""
        try:
            import io
            csv_line = io.StringIO(line)
            reader = csv.reader(csv_line)
            parts = next(reader)
            return [part.strip() for part in parts]
        except:
            if ',' in line:
                return [part.strip() for part in line.split(',')]
            elif '|' in line:
                return [part.strip() for part in line.split('|')]
            else:
                return [line.strip()]
    
    @staticmethod
    def process_word_format(parts):
        """
        处理单词格式：单词、音标、意思、词根和词根意思
        词根列格式示例：
        - "词根struct-（建造、构筑）；后缀-ure（名词后缀）；后缀-ed（形容词后缀）"
        """
        english = parts[0].strip() if len(parts) > 0 else ""
        phonetic = parts[1].strip() if len(parts) > 1 else ""
        chinese = parts[2].strip() if len(parts) > 2 else ""
        root_info = parts[3].strip() if len(parts) > 3 else ""
        
        if not english:
            return None
        
        # 解析词根信息，提取主要词根
        root_word, root_meaning = CSVReader.parse_root_info(root_info)
        
        return {
            'english': english,
            'phonetic': phonetic,
            'chinese': chinese,
            'root_info': root_info,  # 保存完整的词根信息
            'root_word': root_word,
            'root_meaning': root_meaning,
            'is_phrase': False
        }
    
    @staticmethod
    def parse_root_info(root_info):
        """解析词根信息，提取主要词根和意思"""
        root_word = ""
        root_meaning = ""
        
        if not root_info:
            return root_word, root_meaning
        
        # 尝试提取词根
        patterns = [
            r'词根([^；;]+)',
            r'root\s+([^；;]+)',
            r'([a-zA-Z]+)-[（(]',
            r'([a-zA-Z]+)\s+[（(]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, root_info)
            if match:
                root_word = match.group(1).strip()
                break
        
        # 如果没有提取到词根，尝试取前几个字符
        if not root_word and root_info:
            words = re.findall(r'[a-zA-Z]+', root_info)
            if words:
                root_word = words[0]
        
        # 尝试提取意思
        meaning_patterns = [
            r'[（(]([^）)]+)[）)]',
            r'“([^”]+)”',
            r'[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in meaning_patterns:
            match = re.search(pattern, root_info)
            if match:
                root_meaning = match.group(1).strip()
                break
        
        return root_word, root_meaning
    
    @staticmethod
    def process_phrase_format(parts):
        """
        处理词组格式：词组、音标、意思、组成词组的单词和意思
        示例：table salt,/ˈteɪbl sɔːlt/,食用盐,table (n. 桌子；餐桌) + salt (n. 盐)
        """
        english = parts[0].strip() if len(parts) > 0 else ""
        phonetic = parts[1].strip() if len(parts) > 1 else ""
        meaning = parts[2].strip() if len(parts) > 2 else ""
        word_meanings = parts[3].strip() if len(parts) > 3 else ""
        
        if not english:
            return None
        
        return {
            'english': english,
            'phonetic': phonetic,
            'chinese': meaning,
            'word_meanings': word_meanings,
            'is_phrase': True
        }
    
    @staticmethod
    def generate_sample_word_csv():
        """生成示例单式CSV"""
        return """单式,音标,意思,语素
structured,['strʌktʃəd],adj.结构化的；有条理的,词根struct-（建造、构筑）；后缀-ure（名词后缀）；后缀-ed（形容词后缀）
visible,/'vɪzəbl/,adj. 可见的,词根vid-（看）；后缀-ible（可...的）
constructive,/kənˈstrʌktɪv/,adj. 建设性的,词根struct-（建造）；前缀con-（共同）；后缀-ive（形容词）
destruction,/dɪˈstrʌkʃən/,n. 破坏,词根struct-（建造）；前缀de-（向下）；后缀-ion（名词）
instruct,/ɪnˈstrʌkt/,v. 教导,词根struct-（建造）；前缀in-（向内）
biology,/baɪˈɑːlədʒi/,n. 生物学,词根bio-（生命）；后缀-logy（学科）
telephone,/ˈtelɪfoʊn/,n. 电话,词根tele-（远）；词根phon-（声音）
import,/ɪmˈpɔːrt/,v. 进口,词根port-（搬运）；前缀im-（向内）
export,/ˈekspɔːrt/,v. 出口,词根port-（搬运）；前缀ex-（向外）
transport,/trænˈspɔːrt/,v. 运输,词根port-（搬运）；前缀trans-（横穿）"""
    
    @staticmethod
    def generate_sample_phrase_csv():
        """生成示例复式CSV"""
        return """复式,音标,意思,组成复式的单式和意思
table salt,/'teɪbl sɔːlt/,食用盐,table (n. 桌子；餐桌) + salt (n. 盐)
look forward to,/lʊk 'fɔːrwərd tuː/,期待,look (看) + forward (向前) + to (到)
get along with,/ɡet əˈlɔːŋ wɪð/,与...相处,get (得到) + along (沿着) + with (和)
break down,/breɪk daʊn/,出故障,break (打破) + down (向下)
come up with,/kʌm ʌp wɪð/,想出,come (来) + up (向上) + with (和)
run out of,/rʌn aʊt ʌv/,用完,run (跑) + out (出去) + of (的)
take care of,/teɪk ker ʌv/,照顾,take (拿) + care (关心) + of (的)
put off,/pʊt ɔːf/,推迟,put (放) + off (离开)
give up,/ɡɪv ʌp/,放弃,give (给) + up (向上)
turn on,/tɜːrn ɒn/,打开,turn (转动) + on (上面)"""