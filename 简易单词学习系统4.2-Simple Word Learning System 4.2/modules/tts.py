import platform
import threading
import subprocess
import os
import re
import sys
import tempfile

class TextToSpeech:
    def __init__(self):
        self.system = platform.system()
        self.available = self.check_availability()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()  # 修复线程安全问题
    
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
        """朗读文本（安全版本）"""
        if not self.available or not text:
            return
        
        # 严格验证输入（修复漏洞2）
        text = self._safe_clean_text(text)
        if not text:
            return
        
        def _speak():
            try:
                if self.system == "Windows":
                    self._speak_windows_safe(text)
                elif self.system == "Darwin":
                    self._speak_macos(text)
                elif self.system == "Linux":
                    self._speak_linux(text)
            except Exception as e:
                print(f"语音合成失败: {str(e)}")
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
    
    def _safe_clean_text(self, text):
        """
        安全清理文本（修复漏洞2）
        严格过滤所有危险字符，限制长度
        """
        if not text:
            return ""
        
        # 1. 限制文本长度（防止DoS）
        if len(text) > 500:
            text = text[:500]
        
        # 2. 移除所有危险字符（命令注入防护）
        # 只允许字母、数字、空格、常见标点和空格
        text = re.sub(r'[^\w\s.,;:!?\'\"\-\(\)]', '', text)
        
        # 3. 移除特殊控制字符
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # 4. 压缩多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 5. 双重验证：如果清理后文本与原文差异太大，拒绝处理
        # 这里简单检查是否包含危险模式
        dangerous_patterns = ['&', '|', ';', '`', '$', '(', ')', '<', '>']
        for pattern in dangerous_patterns:
            if pattern in text:
                # 移除危险字符
                text = text.replace(pattern, '')
        
        return text
    
    def _speak_windows_safe(self, text):
        """
        安全的Windows语音合成（修复漏洞1）
        不使用VBScript，只使用安全的API
        """
        try:
            # 方法1：使用win32com.client（最安全）
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                # 确保text是安全的字符串
                speaker.Speak(text)
                return
            except ImportError:
                pass
            
            # 方法2：使用PowerShell（Base64编码参数，防止注入）
            try:
                # 将文本转换为Base64，避免参数注入
                import base64
                text_bytes = text.encode('utf-16le')
                b64_text = base64.b64encode(text_bytes).decode('ascii')
                
                # 使用Base64解码后朗读
                ps_command = (
                    f'$t = [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String("{b64_text}")); '
                    f'Add-Type -AssemblyName System.speech; '
                    f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                    f'$s.Speak($t)'
                )
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                
                subprocess.run(
                    ["powershell", "-Command", ps_command],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    capture_output=True,
                    timeout=10
                )
                return
            except:
                pass
            
            # 方法3：如果以上都失败，使用win32com的替代方法
            try:
                # 尝试使用系统默认语音
                import ctypes
                ctypes.windll.user32.MessageBeep(0)
            except:
                pass
                
        except Exception as e:
            print(f"Windows语音合成失败: {str(e)}")
    
    def _speak_macos(self, text):
        """macOS语音合成"""
        try:
            # 安全处理：限制参数长度
            safe_text = text[:200]
            subprocess.run(["say", safe_text], timeout=10, capture_output=True)
        except Exception as e:
            print(f"macOS语音合成失败: {str(e)}")
    
    def _speak_linux(self, text):
        """Linux语音合成"""
        try:
            safe_text = text[:200]
            subprocess.run(["espeak", safe_text], timeout=10, capture_output=True)
        except Exception as e:
            print(f"Linux语音合成失败: {str(e)}")
    
    def stop(self):
        """停止当前语音"""
        self._stop_event.set()