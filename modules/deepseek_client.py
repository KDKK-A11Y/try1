import os
import json
import logging
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("未安装openai库，请执行 pip install openai")


class DeepSeekClient(QObject):
    """DeepSeek API 客户端"""
    
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.client = None
        self._history = []
        
        if OPENAI_AVAILABLE:
            self._init_client()
        else:
            logger.error("OpenAI库未安装，无法初始化DeepSeek客户端")
            self.error_occurred.emit("OpenAI库未安装")
    
    def _init_client(self):
        """初始化DeepSeek客户端"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            logger.info("DeepSeek客户端初始化成功")
        except Exception as e:
            logger.error(f"DeepSeek客户端初始化失败: {str(e)}")
            self.error_occurred.emit(f"初始化失败: {str(e)}")
    
    def set_system_prompt(self, prompt):
        """设置系统提示词"""
        self._history = [{"role": "system", "content": prompt}]
    
    def chat(self, message):
        """发送消息并获取响应"""
        if not self.client:
            logger.error("DeepSeek客户端未初始化")
            self.error_occurred.emit("DeepSeek客户端未初始化")
            return None
        
        try:
            self._history.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=self._history,
                stream=False,
                reasoning_effort="high"
            )
            
            answer = response.choices[0].message.content
            self._history.append({"role": "assistant", "content": answer})
            
            logger.info(f"DeepSeek响应: {answer[:50]}...")
            self.response_received.emit(answer)
            
            return answer
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            self.error_occurred.emit(str(e))
            return None
    
    def clear_history(self):
        """清空对话历史"""
        self._history = []
        logger.info("DeepSeek对话历史已清空")
    
    def get_history(self):
        """获取对话历史"""
        return self._history