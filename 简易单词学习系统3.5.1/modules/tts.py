import platform
import threading
import subprocess
import os
import re
import sys

class TextToSpeech:
    def __init__(self):
        self.system = platform.system()
        self.available = self.check_availability()
    
    def check_availability(self):
        """检查系统语音功能"""
        try:
            if self.system == "Windows":
                return True
            elif self.system == "Darwin":
                result = subprocess.run(["which", "say"], capture_output=True)
                return result.returncode == 0
            elif self.system == "Linux":
                result = subprocess.run(["which", "espeak"], capture_output=True)
                return result.returncode == 0
            return False
        except:
            return False
    
    def speak(self, text):
        """朗读文本"""
        if not self.available or not text:
            return
        
        text = self.clean_text(text)
        
        def _speak():
            try:
                if self.system == "Windows":
                    self._speak_windows(text)
                elif self.system == "Darwin":
                    self._speak_macos(text)
                elif self.system == "Linux":
                    self._speak_linux(text)
            except Exception as e:
                print(f"语音合成失败: {str(e)}")
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
    
    def clean_text(self, text):
        """清理文本"""
        if not text:
            return ""
        text = text.replace('/', '').replace('#', '')
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'【.*?】', '', text)
        text = text.replace('"', '').replace("'", "")
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _speak_windows(self, text):
        """Windows语音合成 - 不弹出cmd窗口"""
        try:
            # 方法1：使用win32com.client（推荐，不弹窗）
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                return
            except ImportError:
                pass
            
            # 方法2：使用PowerShell（隐藏窗口）
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                
                # 转义文本中的双引号
                escaped_text = text.replace('"', '`"')
                ps_command = f'Add-Type -AssemblyName System.speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{escaped_text}")'
                
                subprocess.run(
                    ["powershell", "-Command", ps_command],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    capture_output=True,
                    timeout=10,
                    shell=True
                )
                return
            except:
                pass
            
            # 方法3：使用VBScript（隐藏窗口）
            try:
                # 获取临时目录
                temp_dir = os.environ.get('TEMP', os.path.expanduser('~'))
                vbs_path = os.path.join(temp_dir, "temp_speak.vbs")
                
                vbs_code = f'CreateObject("SAPI.SpVoice").Speak "{text}"'
                with open(vbs_path, "w", encoding="gbk") as f:
                    f.write(vbs_code)
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                
                subprocess.run(
                    ["cscript", "//Nologo", "//B", vbs_path],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    capture_output=True,
                    timeout=10
                )
                if os.path.exists(vbs_path):
                    os.remove(vbs_path)
            except:
                pass
                
        except Exception as e:
            print(f"Windows语音合成失败: {str(e)}")
    
    def _speak_macos(self, text):
        """macOS语音合成"""
        try:
            subprocess.run(["say", text], timeout=10, capture_output=True)
        except Exception as e:
            print(f"macOS语音合成失败: {str(e)}")
    
    def _speak_linux(self, text):
        """Linux语音合成"""
        try:
            subprocess.run(["espeak", text], timeout=10, capture_output=True)
        except Exception as e:
            print(f"Linux语音合成失败: {str(e)}")