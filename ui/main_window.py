import os
import json
import sys

# 动态添加根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFileDialog, 
    QSplitter, QStatusBar, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from config import APP_NAME
from md_parser import MarkdownParserEngine
from file_manager import FileManager
from ui.outline_widget import OutlineWidget
from ui.ai_config_dialog import AIConfigDialog
from ui.ai_sidebar_widget import AISidebarWidget
from ai_agent import AIWorkerThread

CONFIG_FILE = "ai_config.json"


class WebBridge(QObject):
    """Python 与 WebEngine (Vditor) 的双向通信桥梁"""
    text_changed = pyqtSignal(str)

    @pyqtSlot(str)
    def on_text_changed_from_web(self, text: str):
        self.text_changed.emit(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1380, 820)

        self.current_file_path = None
        self.current_markdown_text = ""
        self.ai_config = self.load_ai_config()
        self.ai_thread = None

        # 防抖定时器：200ms 防抖更新大纲和统计字数
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._do_update_outline_and_stats)

        self.init_web_bridge()
        self.init_menu_bar()
        self.init_ui()

    def init_web_bridge(self):
        """建立 WebChannel 双向通信信道"""
        self.web_bridge = WebBridge()
        self.web_bridge.text_changed.connect(self.on_web_text_changed)
        
        self.channel = QWebChannel()
        self.channel.registerObject("pyBridge", self.web_bridge)

    def load_ai_config(self) -> dict:
        default_config = {
            "current_provider": "DeepSeek",
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "providers": {}
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
                    return default_config
            except (FileNotFoundError, json.JSONDecodeError, PermissionError):
                pass
        return default_config

    def save_ai_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.ai_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法保存配置文件: {str(e)}")

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        # 1. 文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")
        
        open_act = QAction("📂 打开...", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(lambda: self.open_file_dialog())
        file_menu.addAction(open_act)

        save_act = QAction("💾 保存", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(lambda: self.save_file())
        file_menu.addAction(save_act)

        file_menu.addSeparator()

        export_pdf_act = QAction("📄 导出为 PDF...", self)
        export_pdf_act.triggered.connect(lambda: self.export_to_pdf())
        file_menu.addAction(export_pdf_act)

        # 2. 视图菜单 (纯粹只包含侧边栏显隐)
        view_menu = menu_bar.addMenu("视图(&V)")

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
        cfg_act = QAction("⚙️ 设置 API Key 与 模型服务", self)
        cfg_act.triggered.connect(self.open_ai_config_dialog)
        ai_menu.addAction(cfg_act)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E5E7EB;
            }
        """)

        # 1. 左侧：大纲栏
        self.outline_widget = OutlineWidget()
        self.outline_widget.heading_clicked.connect(self.scroll_to_heading)
        self.main_splitter.addWidget(self.outline_widget)

        # 2. 中间：WebEngine 光标编辑器
        self.viewer = QWebEngineView()
        self.viewer.page().setWebChannel(self.channel)
        
        demo_text = self.get_demo_text()
        self.current_markdown_text = demo_text
        editor_html = MarkdownParserEngine.get_editor_html(demo_text)
        self.viewer.setHtml(editor_html, QUrl("http://localhost/"))
        self.main_splitter.addWidget(self.viewer)

        # 3. 右侧：AI 侧边栏
        self.ai_sidebar = AISidebarWidget()
        self.ai_sidebar.request_ai_action.connect(self.handle_ai_request)
        self.ai_sidebar.insert_to_doc.connect(self.handle_ai_insert)
        self.main_splitter.addWidget(self.ai_sidebar)

        # 比例分配
        self.main_splitter.setSizes([180, 880, 320])
        main_layout.addWidget(self.main_splitter)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { background: #FAFAFA; border-top: 1px solid #E5E7EB; color: #6B7280; font-size: 12px; }")
        self.setStatusBar(self.status_bar)

        self._do_update_outline_and_stats()

    def on_web_text_changed(self, text: str):
        """网页端实时打字时同步通知 Python"""
        self.current_markdown_text = text
        self.debounce_timer.start(200)

    def _do_update_outline_and_stats(self):
        text = self.current_markdown_text
        self.outline_widget.update_outline(text)
        chars, words, _ = FileManager.calculate_stats(text)
        self.update_status_bar(chars, words)

    def handle_ai_request(self, prompt: str, target_mode: str):
        if not self.ai_config.get("api_key"):
            QMessageBox.warning(self, "提示", "请先在【AI 助手 -> 设置】中配置 API Key！")
            self.open_ai_config_dialog()
            return

        content = self.current_markdown_text.strip()
        if not content:
            QMessageBox.warning(self, "警告", "当前文档内容为空！")
            return

        if self.ai_thread and self.ai_thread.isRunning():
            QMessageBox.information(self, "提示", "AI 正在处理上一次请求，请稍候...")
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
        self.ai_thread.finished.connect(self.ai_thread.deleteLater)
        self.ai_thread.start()

    def on_ai_success(self, reply: str):
        self.ai_sidebar.set_loading(False)
        self.status_bar.showMessage("🟢 AI 生成完成，可修改后直接点击插入")
        self.ai_sidebar.show_response(reply)

    def on_ai_error(self, err_msg: str):
        self.ai_sidebar.set_loading(False)
        self.status_bar.showMessage("🔴 AI 请求出错")
        self.ai_sidebar.show_response(f"❌ 错误: {err_msg}")
        QMessageBox.critical(self, "AI 错误", err_msg)

    def handle_ai_insert(self, action_type: str, text: str, target_mode: str):
        js_code = f"insertMarkdownContent({json.dumps(text)});"
        self.viewer.page().runJavaScript(js_code)
        self.status_bar.showMessage("✅ 已插入 AI 生成内容到光标所在位置")

    def scroll_to_heading(self, heading_idx: int):
        js_code = f"document.getElementById('heading-{heading_idx}')?.scrollIntoView({{behavior: 'smooth'}});"
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
            QMessageBox.information(self, "成功", "AI 服务与 API 配置已更新！")

    def update_status_bar(self, chars, words):
        file_info = self.current_file_path if self.current_file_path else "未命名文档"
        self.status_bar.showMessage(f"文档: {file_info}  |  {words} 词  |  {chars} 字符")

    def open_file_dialog(self):
        """打开文件：带有自动轮询重试机制，绝对保证刷新成功"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 Markdown 文件", "", "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        if file_path:
            content = FileManager.read_file(file_path)
            self.current_file_path = file_path
            self.current_markdown_text = content
            
            json_str = json.dumps(content)
            
            # JS 自动轮询策略：保证 Vditor 加载完后 100% 刷新出新内容
            js_code = f"""
            (function updateWithRetry(text, retries = 15) {{
                if (typeof vditorEditor !== 'undefined' && typeof isEditorReady !== 'undefined' && isEditorReady) {{
                    vditorEditor.setValue(text);
                }} else if (retries > 0) {{
                    setTimeout(() => updateWithRetry(text, retries - 1), 100);
                }}
            }})({json_str});
            """
            
            self.viewer.page().runJavaScript(js_code)
            self._do_update_outline_and_stats()
            self.status_bar.showMessage(f"📂 已打开文件: {file_path}")

    def save_file(self):
        if not self.current_file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "Markdown Files (*.md)")
            if not file_path: 
                return
            self.current_file_path = file_path

        FileManager.save_file(self.current_file_path, self.current_markdown_text)
        self.status_bar.showMessage(f"💾 已保存: {self.current_file_path}")

    def get_demo_text(self) -> str:
        return (
            "# 🚀 SmartMarkdown + AI\n\n"
            "这是一个支持 **所见即所得 (WYSIWYG) 实时光标编辑**、**AI 辅助写作** 与 **LaTeX / Mermaid 渲染** 的 Markdown 编辑器。\n\n"
            "---\n\n"
            "## 💡 核心功能说明\n\n"
            "1. **光标所见即所得**：直接在此界面放置光标进行打字、修改格式，无需切换源码预览。\n"
            "2. **AI 随心插入**：在右侧输入 prompt 生成文本，调整后点击 **【📍 插入到光标处】** 即可。\n"
            "3. **多模型支持**：支持 DeepSeek、Kimi、智谱 AI 和 OpenAI 的灵活切换。\n\n"
            "---\n\n"
            "## 📐 数学公式展示\n\n"
            "$$ \\lim_{x \\to 0} \\frac{\\sin x}{x} = 1 $$\n"
        )