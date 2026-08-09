# ai_agent.py
import requests
from PyQt6.QtCore import QThread, pyqtSignal

class AIWorkerThread(QThread):
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, api_key: str, base_url: str, model: str, prompt: str, content: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.prompt = prompt
        self.content = content

    def run(self):
        if not self.api_key:
            self.error_signal.emit("请先配置有效的 API Key！")
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的 Markdown 智能写作与拆书助手。"},
                {"role": "user", "content": f"{self.prompt}:\n\n{self.content}"}
            ]
        }

        url = f"{self.base_url}/chat/completions"
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                res_json = response.json()
                reply = res_json['choices'][0]['message']['content']
                self.finished_signal.emit(reply)
            else:
                self.error_signal.emit(f"请求失败 ({response.status_code}): {response.text}")
        except Exception as e:
            self.error_signal.emit(f"连接 API 异常: {str(e)}")