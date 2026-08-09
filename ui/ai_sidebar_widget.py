# ui/ai_sidebar_widget.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

class AISidebarWidget(QWidget):
    # 信号定义：request_ai_action(prompt, target_mode), insert_to_doc(action_type, text, target_mode)
    request_ai_action = pyqtSignal(str, str)
    insert_to_doc = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # 1. 顶部标题栏
        header_layout = QHBoxLayout()
        title_label = QLabel("✨ AI 创作助手")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 2. 当前模式说明提示框 (已移除源码/渲染二选一切按钮)
        mode_hint = QLabel("当前模式：📖 所见即所得编辑")
        mode_hint.setStyleSheet("""
            background-color: #F3F4F6;
            color: #4B5563;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(mode_hint)

        # 分割线
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("color: #E5E7EB;")
        layout.addWidget(line1)

        # 3. 快捷写作指令区
        quick_label = QLabel("快捷写作")
        quick_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #6B7280;")
        layout.addWidget(quick_label)

        btn_summary = QPushButton("📝 生成全文摘要")
        btn_summary.clicked.connect(lambda: self.on_quick_action("请帮我总结当前文档的核心要点并生成全文摘要。"))

        btn_expand = QPushButton("💡 扩写与细节丰富")
        btn_expand.clicked.connect(lambda: self.on_quick_action("请对当前文档内容进行扩写，补充更多细节和逻辑支撑。"))

        btn_polish = QPushButton("✨ 文章润色与纠错")
        btn_polish.clicked.connect(lambda: self.on_quick_action("请纠正当前文档中的错别字与语法错误，并润色语句使其更流畅。"))

        for btn in (btn_summary, btn_expand, btn_polish):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        # 4. 自定义指令区
        custom_label = QLabel("自定义指令")
        custom_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #6B7280;")
        layout.addWidget(custom_label)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("例如: 总结核心要点 / 翻译为英文...")
        self.prompt_edit.setFixedHeight(70)
        layout.addWidget(self.prompt_edit)

        self.send_btn = QPushButton("发送指令")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self.on_send_custom_prompt)
        layout.addWidget(self.send_btn)

        # 进度条 (默认隐藏)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 5. AI 生成结果展现区
        result_label = QLabel("AI 生成文本 (可修改)")
        result_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #6B7280;")
        layout.addWidget(result_label)

        self.response_edit = QTextEdit()
        self.response_edit.setPlaceholderText("AI 处理内容将在此呈现，你可以直接编辑修改...")
        layout.addWidget(self.response_edit)

        # 6. 底部插入操作按钮
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.insert_btn = QPushButton("📍 插入到光标处")
        self.insert_btn.setObjectName("insertBtn")
        self.insert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.insert_btn.clicked.connect(
            lambda: self.on_insert_action("insert_at_cursor")
        )

        self.append_btn = QPushButton("➕ 追加到文本")
        self.append_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.append_btn.clicked.connect(
            lambda: self.on_insert_action("append_end")
        )

        action_layout.addWidget(self.insert_btn)
        action_layout.addWidget(self.append_btn)
        layout.addLayout(action_layout)

    def on_quick_action(self, prompt_text: str):
        """触发快捷写作指令"""
        self.request_ai_action.emit(prompt_text, "rendered")

    def on_send_custom_prompt(self):
        """发送自定义指令"""
        prompt = self.prompt_edit.toPlainText().strip()
        if prompt:
            self.request_ai_action.emit(prompt, "rendered")

    def on_insert_action(self, action_type: str):
        """触发插入到正文"""
        text = self.response_edit.toPlainText()
        if text.strip():
            self.insert_to_doc.emit(action_type, text, "rendered")

    def show_response(self, text: str):
        """展示 AI 返回的结果"""
        self.set_loading(False)
        self.response_edit.setPlainText(text)

    def set_loading(self, loading: bool):
        """设置加载状态"""
        if loading:
            self.progress_bar.show()
            self.send_btn.setEnabled(False)
            self.send_btn.setText("⏳ AI 思考中...")
        else:
            self.progress_bar.hide()
            self.send_btn.setEnabled(True)
            self.send_btn.setText("发送指令")

    def apply_styles(self):
        """界面 QSS 美化"""
        self.setStyleSheet("""
            AISidebarWidget {
                background-color: #FAFAFA;
                border-left: 1px solid #E5E7EB;
            }
            QTextEdit {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                background-color: #FFFFFF;
                padding: 8px;
                font-size: 13px;
                color: #1F2937;
            }
            QTextEdit:focus {
                border: 1px solid #2563EB;
            }
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: #374151;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
                border-color: #D1D5DB;
            }
            QPushButton#sendBtn {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                text-align: center;
                font-weight: bold;
            }
            QPushButton#sendBtn:hover {
                background-color: #1D4ED8;
            }
            QPushButton#sendBtn:disabled {
                background-color: #93C5FD;
            }
            QPushButton#insertBtn {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                text-align: center;
                font-weight: bold;
            }
            QPushButton#insertBtn:hover {
                background-color: #059669;
            }
        """)