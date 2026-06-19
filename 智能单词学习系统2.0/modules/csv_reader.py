import csv
import re

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
                            if '词组' in header or '短语' in header or 'phrase' in header:
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
        处理单词格式：单词、音标、意思、词根(含意思)
        词根列格式：bio 生命 或 bio:生命 或 bio-生命
        """
        english = parts[0].strip() if len(parts) > 0 else ""
        phonetic = parts[1].strip() if len(parts) > 1 else ""
        chinese = parts[2].strip() if len(parts) > 2 else ""
        root_column = parts[3].strip() if len(parts) > 3 else ""
        
        if not english:
            return None
        
        # 解析词根列
        root_word, root_meaning = CSVReader.parse_root_column(root_column)
        
        return {
            'english': english,
            'phonetic': phonetic,
            'chinese': chinese,
            'root_word': root_word,
            'root_meaning': root_meaning,
            'is_phrase': False
        }
    
    @staticmethod
    def parse_root_column(root_column):
        """解析词根列，分离词根和意思"""
        root_word = ""
        root_meaning = ""
        
        if not root_column:
            return root_word, root_meaning
        
        # 尝试各种分隔符
        separators = [' ', ':', '：', '-', '|', '、']
        for sep in separators:
            if sep in root_column:
                parts = root_column.split(sep, 1)
                root_word = parts[0].strip()
                root_meaning = parts[1].strip() if len(parts) > 1 else ""
                return root_word, root_meaning
        
        # 无分隔符，通过中文字符判断
        if re.search('[\u4e00-\u9fff]', root_column):
            root_meaning = root_column
        else:
            root_word = root_column
        
        return root_word, root_meaning
    
    @staticmethod
    def process_phrase_format(parts):
        """
        处理词组格式：词组、音标、意思、单词意思
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
        """生成示例单词CSV"""
        return """单词,音标,意思,词根
apple,/ˈæpl/,苹果,
beautiful,/ˈbjuːtɪfl/,美丽的,beauty 美
computer,/kəmˈpjuːtər/,电脑,pute 思考
run,/rʌn/,跑步,
happy,/ˈhæpi/,快乐的,
big,/bɪɡ/,大的,
small,/smɔːl/,小的,
biology,/baɪˈɑːlədʒi/,生物学,bio 生命
telephone,/ˈtelɪfoʊn/,电话,tel 远
visible,/ˈvɪzəbl/,可见的,vid 看
educate,/ˈedʒukeɪt/,教育,e 出 + duc 引导
import,/ɪmˈpɔːrt/,进口,im 进入 + port 搬运
export,/ˈekspɔːrt/,出口,ex 出 + port 搬运
predict,/prɪˈdɪkt/,预测,pre 预先 + dict 说"""
    
    @staticmethod
    def generate_sample_phrase_csv():
        """生成示例词组CSV"""
        return """词组,音标,意思,单词意思
look forward to,/lʊk ˈfɔːrwərd tuː/,期待,看-向前-到
get along with,/ɡet əˈlɔːŋ wɪð/,与...相处,得到-沿着-和
break down,/breɪk daʊn/,出故障,打破-向下
come up with,/kʌm ʌp wɪð/,想出,来-向上-和
run out of,/rʌn aʊt ʌv/,用完,跑-出去-的
take care of,/teɪk ker ʌv/,照顾,拿-关心-的
put off,/pʊt ɔːf/,推迟,放-离开
give up,/ɡɪv ʌp/,放弃,给-向上"""