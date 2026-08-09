import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox,
    QGroupBox, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# 预设厂商标准默认配置
PRESET_PROVIDERS = {
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat"
    },
    "Kimi (Moonshot)": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k"
    },
    "智谱 AI (GLM)": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash"
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini"
    },
    "自定义 (Custom)": {
        "base_url": "",
        "model": ""
    }
}

class AIConfigDialog(QDialog):
    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ AI 模型与 API 配置")
        self.setMinimumWidth(480)
        
        # 深拷贝或处理传入配置，支持Providers历史字典结构
        self.config_data = current_config if current_config else {}
        self.providers_history = self.config_data.get("providers", {})
        
        # 兼容旧版本单厂商格式，同步写入历史记录中
        current_provider = self.config_data.get("current_provider", "DeepSeek")
        if "api_key" in self.config_data and current_provider not in self.providers_history:
            self.providers_history[current_provider] = {
                "api_key": self.config_data.get("api_key", ""),
                "base_url": self.config_data.get("base_url", PRESET_PROVIDERS["DeepSeek"]["base_url"]),
                "model": self.config_data.get("model", PRESET_PROVIDERS["DeepSeek"]["model"])
            }

        self.last_selected_provider = current_provider
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 头部说明
        header_label = QLabel("配置 AI 大语言模型服务商及其 API Key 参数：")
        header_label.setStyleSheet("color: #4B5563; font-weight: bold; font-size: 13px;")
        main_layout.addWidget(header_label)

        # 主配置分组框
        group_box = QGroupBox("服务商参数设置")
        form_layout = QFormLayout(group_box)
        form_layout.setSpacing(14)

        # 1. 服务商下拉框
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(list(PRESET_PROVIDERS.keys()))
        form_layout.addRow("选择服务商:", self.provider_combo)

        # 2. API Key 输入框 (附带明文/密文切换按钮)
        key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("在此粘贴 API Key (如 sk-...)")
        
        self.toggle_key_btn = QToolButton()
        self.toggle_key_btn.setText("👁️")
        self.toggle_key_btn.setToolTip("显示/隐藏 API Key")
        self.toggle_key_btn.setCheckable(True)
        self.toggle_key_btn.toggled.connect(self.toggle_api_key_visibility)

        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(self.toggle_key_btn)
        form_layout.addRow("API Key:", key_layout)

        # 3. Base URL 输入框
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.example.com/v1")
        form_layout.addRow("Base URL:", self.base_url_input)

        # 4. Model 名称输入框
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("例如: moonshot-v1-8k / glm-4-flash")
        form_layout.addRow("模型 (Model):", self.model_input)

        main_layout.addWidget(group_box)

        # 初始选中服务商并填充数据
        if self.last_selected_provider in PRESET_PROVIDERS:
            self.provider_combo.setCurrentText(self.last_selected_provider)
        self.load_provider_data(self.provider_combo.currentText())

        # 绑定切换服务商信号（自动缓存上个服务商并加载新服务商/清空残留Key）
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        # 5. 底部按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("保存配置")
        save_btn.setObjectName("saveBtn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.on_save)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)

    def toggle_api_key_visibility(self, checked: bool):
        """明文/密文切换"""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("👁️")

    def on_provider_changed(self, new_provider: str):
        """核心修复：切换服务商时保存当前数据并正确重置/加载新服务商的 API Key"""
        # 1. 暂存当前正在离开的服务商数据到内存字典中
        if self.last_selected_provider:
            self.providers_history[self.last_selected_provider] = {
                "api_key": self.api_key_input.text().strip(),
                "base_url": self.base_url_input.text().strip(),
                "model": self.model_input.text().strip()
            }

        # 2. 加载新服务商配置
        self.load_provider_data(new_provider)
        self.last_selected_provider = new_provider

    def load_provider_data(self, provider_name: str):
        """读取服务商的历史配置，若无则使用默认预设并将 Key 清空"""
        preset = PRESET_PROVIDERS.get(provider_name, {"base_url": "", "model": ""})
        
        if provider_name in self.providers_history:
            # 存在历史填写的 key 则加载历史记录
            history = self.providers_history[provider_name]
            self.api_key_input.setText(history.get("api_key", ""))
            self.base_url_input.setText(history.get("base_url") or preset["base_url"])
            self.model_input.setText(history.get("model") or preset["model"])
        else:
            # 不存在历史记录：彻底清空 API Key，自动填入官方推荐 Base URL 和 Model
            self.api_key_input.clear()
            self.base_url_input.setText(preset["base_url"])
            self.model_input.setText(preset["model"])

    def on_save(self):
        """保存时收集数据"""
        # 确保当前界面的最新配置被暂存
        current_provider = self.provider_combo.currentText()
        self.providers_history[current_provider] = {
            "api_key": self.api_key_input.text().strip(),
            "base_url": self.base_url_input.text().strip(),
            "model": self.model_input.text().strip()
        }
        self.accept()

    def get_config(self) -> dict:
        """返回结构化数据给 MainWindow 保存"""
        current_provider = self.provider_combo.currentText()
        active_info = self.providers_history.get(current_provider, {})
        
        return {
            "current_provider": current_provider,
            "api_key": active_info.get("api_key", ""),
            "base_url": active_info.get("base_url", ""),
            "model": active_info.get("model", ""),
            "providers": self.providers_history  # 保持所有服务商历史密钥分立存储
        }

    def apply_styles(self):
        """界面美化 QSS"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 6px;
                padding-top: 12px;
                background-color: #FAFAFA;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #374151;
            }
            QLineEdit, QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #111827;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2563EB;
            }
            QToolButton {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                background-color: #F3F4F6;
                padding: 4px 8px;
            }
            QPushButton {
                padding: 7px 18px;
                border-radius: 6px;
                border: 1px solid #D1D5DB;
                background-color: #FFFFFF;
                color: #374151;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
            }
            QPushButton#saveBtn {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background-color: #1D4ED8;
            }
        """)