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
        处理单词格式：单词、音标、意思、词根和词根意思、例句英文、例句中文
        共6列
        """
        english = parts[0].strip() if len(parts) > 0 else ""
        phonetic = parts[1].strip() if len(parts) > 1 else ""
        chinese = parts[2].strip() if len(parts) > 2 else ""
        root_info = parts[3].strip() if len(parts) > 3 else ""
        example = parts[4].strip() if len(parts) > 4 else ""
        example_cn = parts[5].strip() if len(parts) > 5 else ""
        
        if not english:
            return None
        
        # 解析词根信息，提取主要词根
        root_word, root_meaning = CSVReader.parse_root_info(root_info)
        
        return {
            'english': english,
            'phonetic': phonetic,
            'chinese': chinese,
            'root_info': root_info,
            'root_word': root_word,
            'root_meaning': root_meaning,
            'example': example,
            'example_cn': example_cn,
            'is_phrase': False
        }
    
    @staticmethod
    def parse_root_info(root_info):
        """解析词根信息，提取主要词根和意思"""
        root_word = ""
        root_meaning = ""
        
        if not root_info:
            return root_word, root_meaning
        
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
        
        if not root_word and root_info:
            words = re.findall(r'[a-zA-Z]+', root_info)
            if words:
                root_word = words[0]
        
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
        处理词组格式：词组、音标、意思、组成词组的单词和意思、例句英文、例句中文
        共6列
        """
        english = parts[0].strip() if len(parts) > 0 else ""
        phonetic = parts[1].strip() if len(parts) > 1 else ""
        meaning = parts[2].strip() if len(parts) > 2 else ""
        word_meanings = parts[3].strip() if len(parts) > 3 else ""
        example = parts[4].strip() if len(parts) > 4 else ""
        example_cn = parts[5].strip() if len(parts) > 5 else ""
        
        if not english:
            return None
        
        return {
            'english': english,
            'phonetic': phonetic,
            'chinese': meaning,
            'word_meanings': word_meanings,
            'example': example,
            'example_cn': example_cn,
            'is_phrase': True
        }
    
    @staticmethod
    def generate_sample_word_csv():
        """生成示例单式CSV（6列：单式,音标,意思,语素,例句英文,例句中文）"""
        return """单式,音标,意思,语素,例句英文,例句中文
structured,['strʌktʃəd],结构化的；有条理的,词根struct-（建造、构筑）；后缀-ure（名词后缀）；后缀-ed（形容词后缀）,The course is well structured.,这门课程结构很好。
visible,/'vɪzəbl/,可见的,词根vid-（看）；后缀-ible（可...的）,The stars are visible tonight.,今晚星星可见。
constructive,/kənˈstrʌktɪv/,建设性的,词根struct-（建造）；前缀con-（共同）；后缀-ive（形容词）,Thank you for your constructive feedback.,感谢您提出建设性的反馈。
destruction,/dɪˈstrʌkʃən/,破坏,词根struct-（建造）；前缀de-（向下）；后缀-ion（名词）,The storm caused widespread destruction.,暴风雨造成了广泛的破坏。
instruct,/ɪnˈstrʌkt/,教导,词根struct-（建造）；前缀in-（向内）,The teacher will instruct us on the topic.,老师将就这个主题给我们指导。
biology,/baɪˈɑːlədʒi/,生物学,词根bio-（生命）；后缀-logy（学科）,She is studying biology at university.,她正在大学学习生物学。
telephone,/ˈtelɪfoʊn/,电话,词根tele-（远）；词根phon-（声音）,I need to make a telephone call.,我需要打个电话。
import,/ɪmˈpɔːrt/,进口,词根port-（搬运）；前缀im-（向内）,The country imports most of its oil.,这个国家大部分石油依赖进口。
export,/ˈekspɔːrt/,出口,词根port-（搬运）；前缀ex-（向外）,China exports many products worldwide.,中国向全球出口许多产品。
transport,/trænˈspɔːrt/,运输,词根port-（搬运）；前缀trans-（横穿）,The pipeline transports natural gas.,这条管道运输天然气。"""
    
    @staticmethod
    def generate_sample_phrase_csv():
        """生成示例复式CSV（6列：复式,音标,意思,组成复式的单式和意思,例句英文,例句中文）"""
        return """复式,音标,意思,组成复式的单式和意思,例句英文,例句中文
table salt,/'teɪbl sɔːlt/,食用盐,table（桌子）+ salt（盐）,Please pass me the table salt.,请把食盐递给我。
look forward to,/lʊk 'fɔːrwərd tuː/,期待,look（看）+ forward（向前）+ to（到）,I look forward to meeting you.,我期待见到你。
get along with,/ɡet əˈlɔːŋ wɪð/,与...相处,get（得到）+ along（沿着）+ with（和）,She gets along with everyone.,她和每个人都相处得很好。
break down,/breɪk daʊn/,出故障,break（打破）+ down（向下）,My car broke down yesterday.,我的车昨天抛锚了。
come up with,/kʌm ʌp wɪð/,想出,come（来）+ up（向上）+ with（和）,He came up with a great idea.,他想出了一个好主意。
run out of,/rʌn aʊt ʌv/,用完,run（跑）+ out（出去）+ of（的）,We have run out of milk.,我们的牛奶喝完了。
take care of,/teɪk ker ʌv/,照顾,take（拿）+ care（关心）+ of（的）,Please take care of my cat.,请帮我照顾我的猫。
put off,/pʊt ɔːf/,推迟,put（放）+ off（离开）,Don't put off your homework.,不要拖延你的作业。
give up,/ɡɪv ʌp/,放弃,give（给）+ up（向上）,Never give up on your dreams.,永远不要放弃你的梦想。
turn on,/tɜːrn ɒn/,打开,turn（转动）+ on（上面）,Please turn on the light.,请把灯打开。"""