# ui/ai_config_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox
)

class AIConfigDialog(QDialog):
    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ 配置 AI 密钥与 API")
        self.resize(450, 220)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.api_key_input = QLineEdit(current_config.get("api_key", ""))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-xxxxxxx")

        self.base_url_input = QLineEdit(current_config.get("base_url", "https://api.deepseek.com/v1"))
        self.model_input = QLineEdit(current_config.get("model", "deepseek-chat"))

        form_layout.addRow("API Key:", self.api_key_input)
        form_layout.addRow("Base URL:", self.base_url_input)
        form_layout.addRow("Model 名称:", self.model_input)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_config(self) -> dict:
        return {
            "api_key": self.api_key_input.text().strip(),
            "base_url": self.base_url_input.text().strip(),
            "model": self.model_input.text().strip()
        }