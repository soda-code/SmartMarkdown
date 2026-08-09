# ui/ai_sidebar_widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QMessageBox, QFrame, QButtonGroup
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, Qt

class AISidebarWidget(QWidget):
    request_ai_action = pyqtSignal(str, str)
    insert_to_doc = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.target_mode = "source"  # 默认目标模式："source" 或 "rendered"
        self.init_ui()

    def init_ui(self):
        # 全局现代简约 QSS 样式定义
        self.setStyleSheet("""
            QWidget {
                background-color: #FAFAFA;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
                color: #1F2937;
            }
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #4B5563;
                margin-top: 4px;
            }
            /* 现代卡片按钮 */
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 500;
                color: #374151;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
                border-color: #D1D5DB;
            }
            QPushButton:pressed {
                background-color: #E5E7EB;
            }
            /* 主行动按钮 */
            QPushButton#primaryBtn {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                font-weight: 600;
                text-align: center;
            }
            QPushButton#primaryBtn:hover {
                background-color: #1D4ED8;
            }
            QPushButton#successBtn {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                font-weight: 600;
                text-align: center;
            }
            QPushButton#successBtn:hover {
                background-color: #059669;
            }
            /* 文本框 */
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #1F2937;
            }
            QTextEdit:focus {
                border: 1.5px solid #2563EB;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. 顶部 Header
        header_layout = QHBoxLayout()
        title_label = QLabel("✨ AI 创作助手")
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #111827; font-size: 14px;")
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)

        # 2. 现代风格分段模式选择器 (Segmented Control)
        mode_container = QFrame()
        mode_container.setStyleSheet("background-color: #F3F4F6; border-radius: 8px; padding: 2px;")
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(2, 2, 2, 2)
        mode_layout.setSpacing(2)

        self.btn_mode_source = QPushButton("⚡ 源码模式")
        self.btn_mode_rendered = QPushButton("📖 渲染视图")
        
        for btn in (self.btn_mode_source, self.btn_mode_rendered):
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 6px;
                    padding: 5px 0px;
                    text-align: center;
                    font-size: 11px;
                    color: #6B7280;
                    background-color: transparent;
                }
                QPushButton:checked {
                    background-color: #FFFFFF;
                    color: #111827;
                    font-weight: 600;
                    border: 1px solid #E5E7EB;
                }
            """)

        self.btn_mode_source.setChecked(True)
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.btn_mode_source)
        self.mode_group.addButton(self.btn_mode_rendered)
        self.mode_group.buttonClicked.connect(self.on_mode_changed)

        mode_layout.addWidget(self.btn_mode_source)
        mode_layout.addWidget(self.btn_mode_rendered)
        layout.addWidget(mode_container)

        # 3. 快捷指令区
        layout.addWidget(QLabel("快捷写作"))

        btn_summary = QPushButton("📝 生成全文摘要")
        btn_summary.clicked.connect(lambda: self.on_action_click("请为以下 Markdown 文章生成一份结构清晰的简短摘要"))
        layout.addWidget(btn_summary)

        btn_expand = QPushButton("💡 扩写与细节丰富")
        btn_expand.clicked.connect(lambda: self.on_action_click("请对以下内容进行逻辑扩写，补充细节与丰富表达"))
        layout.addWidget(btn_expand)

        btn_polish = QPushButton("✨ 文章润色与纠错")
        btn_polish.clicked.connect(lambda: self.on_action_click("请对以下 Markdown 文章进行专业润色与语法错别字纠正"))
        layout.addWidget(btn_polish)

        # 4. 自定义 Prompt 区
        layout.addWidget(QLabel("自定义指令"))
        self.custom_prompt_input = QTextEdit()
        self.custom_prompt_input.setPlaceholderText("例如：总结核心要点 / 翻译为英文...")
        self.custom_prompt_input.setMaximumHeight(65)
        layout.addWidget(self.custom_prompt_input)

        btn_custom_send = QPushButton("发送指令")
        btn_custom_send.setObjectName("primaryBtn")
        btn_custom_send.clicked.connect(self.on_custom_send)
        layout.addWidget(btn_custom_send)

        # 5. 可编辑 AI 输出结果
        layout.addWidget(QLabel("AI 生成文本 (可修改)"))
        self.ai_output_display = QTextEdit()
        self.ai_output_display.setReadOnly(False)
        self.ai_output_display.setPlaceholderText("AI 处理内容将在此呈现，你可以直接编辑修改...")
        layout.addWidget(self.ai_output_display)

        # 6. 底部随心插入按钮组
        insert_btn_box = QHBoxLayout()
        insert_btn_box.setSpacing(8)

        btn_insert_cursor = QPushButton("📍 插入到光标处")
        btn_insert_cursor.setObjectName("successBtn")
        btn_insert_cursor.clicked.connect(lambda: self.on_insert_click("insert_at_cursor"))

        btn_append_end = QPushButton("➕ 追加到文末")
        btn_append_end.clicked.connect(lambda: self.on_insert_click("append_end"))

        insert_btn_box.addWidget(btn_insert_cursor)
        insert_btn_box.addWidget(btn_append_end)
        layout.addLayout(insert_btn_box)

    def on_mode_changed(self, button):
        if button == self.btn_mode_source:
            self.target_mode = "source"
        else:
            self.target_mode = "rendered"

    def on_action_click(self, prompt: str):
        self.request_ai_action.emit(prompt, self.target_mode)

    def on_custom_send(self):
        prompt = self.custom_prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入自定义指令内容！")
            return
        self.request_ai_action.emit(prompt, self.target_mode)

    def on_insert_click(self, action_type: str):
        text = self.ai_output_display.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "当前 AI 文本框为空，无法插入！")
            return
        self.insert_to_doc.emit(action_type, text, self.target_mode)

    def set_loading(self, loading: bool):
        if loading:
            self.ai_output_display.setText("⏳ AI 正在思考与撰写中...")

    def show_response(self, text: str):
        self.ai_output_display.setText(text)