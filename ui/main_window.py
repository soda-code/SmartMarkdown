# ui/main_window.py
import os
import json
import sys

# 动态添加根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFileDialog, 
    QSplitter, QStatusBar, QMessageBox, QStackedWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QFont, QAction, QKeySequence

from config import APP_NAME
from md_parser import MarkdownParserEngine
from file_manager import FileManager
from ui.outline_widget import OutlineWidget
from ui.text_editor import CodeTextEditor
from ui.ai_config_dialog import AIConfigDialog
from ui.ai_sidebar_widget import AISidebarWidget
from ai_agent import AIWorkerThread

CONFIG_FILE = "ai_config.json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1380, 820)

        self.parser_engine = MarkdownParserEngine()
        self.current_file_path = None
        self.is_source_mode = False
        self.ai_config = self.load_ai_config()

        self.init_menu_bar()
        self.init_ui()

    def load_ai_config(self) -> dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {"api_key": "", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"}

    def save_ai_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.ai_config, f, ensure_ascii=False, indent=2)

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        # 1. 文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")
        open_act = QAction("📂 打开...", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_act)

        save_act = QAction("💾 保存", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self.save_file)
        file_menu.addAction(save_act)

        file_menu.addSeparator()

        export_pdf_act = QAction("📄 导出为 PDF...", self)
        export_pdf_act.triggered.connect(self.export_to_pdf)
        file_menu.addAction(export_pdf_act)

        # 2. 视图菜单
        view_menu = menu_bar.addMenu("视图(&V)")
        self.source_mode_act = QAction("⚡ 切换源码 / 渲染视图 (Ctrl+/)", self)
        self.source_mode_act.setShortcut(QKeySequence("Ctrl+/"))
        self.source_mode_act.triggered.connect(self.toggle_source_mode)
        view_menu.addAction(self.source_mode_act)

        self.toggle_outline_act = QAction("📋 左侧大纲栏", self)
        self.toggle_outline_act.setCheckable(True)
        self.toggle_outline_act.setChecked(True)
        self.toggle_outline_act.triggered.connect(lambda chk: self.outline_widget.setVisible(chk))
        view_menu.addAction(self.toggle_outline_act)

        self.toggle_ai_sidebar_act = QAction("🤖 右侧 AI 侧边栏", self)
        self.toggle_ai_sidebar_act.setCheckable(True)
        self.toggle_ai_sidebar_act.setChecked(True)
        self.toggle_ai_sidebar_act.triggered.connect(lambda chk: self.ai_sidebar.setVisible(chk))
        view_menu.addAction(self.toggle_ai_sidebar_act)

        # 3. AI 菜单
        ai_menu = menu_bar.addMenu("🤖 AI 助手(&A)")
        cfg_act = QAction("⚙️ 设置 API Key 与 Base URL", self)
        cfg_act.triggered.connect(self.open_ai_config_dialog)
        ai_menu.addAction(cfg_act)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        # 统一极简灰色的分割线样式
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E5E7EB;
            }
        """)

        # 1. 最左侧：大纲栏
        self.outline_widget = OutlineWidget()
        self.outline_widget.heading_clicked.connect(self.scroll_to_heading)
        self.main_splitter.addWidget(self.outline_widget)

        # 2. 中间：文档排版区 (堆叠视窗：渲染预览 vs 源码编辑)
        self.work_stack = QStackedWidget()

        self.viewer = QWebEngineView()
        self.work_stack.addWidget(self.viewer)

        self.editor = CodeTextEditor()
        self.editor.textChanged.connect(self.on_text_changed)
        self.work_stack.addWidget(self.editor)

        self.main_splitter.addWidget(self.work_stack)

        # 3. 最右侧：现代极简 AI 侧边栏
        self.ai_sidebar = AISidebarWidget()
        self.ai_sidebar.request_ai_action.connect(self.handle_ai_request)
        self.ai_sidebar.insert_to_doc.connect(self.handle_ai_insert)
        self.main_splitter.addWidget(self.ai_sidebar)

        # 比例分配：大纲 150px : 中间 900px : 右侧 AI 侧边栏 320px
        self.main_splitter.setSizes([150, 900, 320])
        main_layout.addWidget(self.main_splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background: #FAFAFA; border-top: 1px solid #E5E7EB; color: #6B7280; font-size: 12px; }")
        self.setStatusBar(self.status_bar)

        self.load_demo_text()

    def handle_ai_request(self, prompt: str, target_mode: str):
        content = self.editor.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "警告", "当前文档内容为空！")
            return

        self.ai_sidebar.set_loading(True)
        self.status_bar.showMessage("⏳ AI 正在处理侧边栏指令...")

        self.ai_thread = AIWorkerThread(
            api_key=self.ai_config["api_key"],
            base_url=self.ai_config["base_url"],
            model=self.ai_config["model"],
            prompt=prompt,
            content=content
        )
        self.ai_thread.finished_signal.connect(self.on_ai_success)
        self.ai_thread.error_signal.connect(self.on_ai_error)
        self.ai_thread.start()

    def on_ai_success(self, reply: str):
        self.status_bar.showMessage("🟢 AI 生成完成，可以在右侧修改后点击插入")
        self.ai_sidebar.show_response(reply)

    def handle_ai_insert(self, action_type: str, text: str, target_mode: str):
        """处理 AI 文本插入（支持自动切源码定位光标）"""
        formatted_text = f"\n\n{text}\n"

        # 1. 如果在渲染预览模式，自动先切换到源码模式以定位实际光标
        if self.work_stack.currentIndex() == 0:
            self.work_stack.setCurrentIndex(1)
            self.is_source_mode = True

        # 2. 插入光标处或追加到末尾
        if action_type == "insert_at_cursor":
            cursor = self.editor.textCursor()
            cursor.insertText(formatted_text)
        else:
            self.editor.appendPlainText(formatted_text)

        # 3. 如果侧边栏选择的目标模式是“正式文本”，刷新渲染并切回预览
        if target_mode == "rendered":
            self.on_text_changed()
            self.work_stack.setCurrentIndex(0)
            self.is_source_mode = False

        self.status_bar.showMessage("✅ 文本已成功插入指定位置")

    def on_ai_error(self, err_msg: str):
        self.status_bar.showMessage("🔴 AI 请求出错")
        self.ai_sidebar.show_response(f"❌ 错误: {err_msg}")
        QMessageBox.critical(self, "AI 错误", err_msg)

    def scroll_to_heading(self, heading_idx: int):
        js_code = f"document.getElementById('heading-{heading_idx}').scrollIntoView({{behavior: 'smooth'}});"
        self.viewer.page().runJavaScript(js_code)

    def export_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出为 PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.viewer.page().printToPdf(file_path)
            self.status_bar.showMessage(f"✅ 已导出 PDF: {file_path}")

    def open_ai_config_dialog(self):
        dialog = AIConfigDialog(self.ai_config, self)
        if dialog.exec() == AIConfigDialog.DialogCode.Accepted:
            self.ai_config = dialog.get_config()
            self.save_ai_config()
            QMessageBox.information(self, "成功", "AI 密钥与 API 配置已保存！")

    def on_text_changed(self):
        raw_text = self.editor.toPlainText()
        html_text = self.parser_engine.parse(raw_text)
        self.viewer.setHtml(html_text, QUrl("http://localhost/"))
        self.outline_widget.update_outline(raw_text)
        chars, words, read_time = FileManager.calculate_stats(raw_text)
        self.update_status_bar(chars, words)

    def toggle_source_mode(self):
        self.is_source_mode = not self.is_source_mode
        if self.is_source_mode:
            self.work_stack.setCurrentIndex(1)
            self.status_bar.showMessage("⚡ 视图：源代码模式")
        else:
            self.work_stack.setCurrentIndex(0)
            self.on_text_changed()

    def update_status_bar(self, chars, words):
        mode_str = "[源码模式] " if self.is_source_mode else "[渲染模式] "
        file_info = self.current_file_path if self.current_file_path else "未命名文档"
        self.status_bar.showMessage(f"{mode_str}{file_info}  |  {words} 词  |  {chars} 字符")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 Markdown 文件", "", "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        if file_path:
            content = FileManager.read_file(file_path)
            self.current_file_path = file_path
            self.editor.setPlainText(content)

    def save_file(self):
        if not self.current_file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "Markdown Files (*.md)")
            if not file_path: return
            self.current_file_path = file_path
        FileManager.save_file(self.current_file_path, self.editor.toPlainText())

    def load_demo_text(self):
        demo_md = (
            "# 🚀 Typora Deep Clone + AI\n\n"
            "这是一个拥有 **现代 UI 侧边栏**、**AI 文本二次编辑** 与 **随心光标插入** 的 Markdown 阅读器。\n\n"
            "---\n\n"
            "## 💡 核心功能说明\n\n"
            "1. **随心插入**：点击右侧 AI 指令生成内容，直接在右侧文本框修改后，点击 **【📍 插入到光标处】** 即可。\n"
            "2. **分段模式控制**：右侧顶部的按钮可让你选择 AI 结果是同步流向 **⚡ 源码模式** 还是 **📖 渲染视图**。\n"
            "3. **快捷快捷键**：按 `Ctrl + /` 可快速在源码编辑与预览模式间来回切换。\n\n"
            "---\n\n"
            "## 📐 数学公式展示\n\n"
            "$$ \\lim_{x \\to 0} \\frac{\\sin x}{x} = 1 $$\n"
        )
        self.editor.setPlainText(demo_md)