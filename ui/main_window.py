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

from config import APP_NAME, THEME_CSS
from md_parser import MarkdownParserEngine
from file_manager import FileManager
from ui.outline_widget import OutlineWidget
from ui.ai_config_dialog import AIConfigDialog
from ui.ai_sidebar_widget import AISidebarWidget
from ai_agent import AIWorkerThread

CONFIG_FILE = "ai_config.json"

# ── 菜单栏样式（与整体 UI 风格统一） ──────────────
MENU_QSS = """
    QMenuBar {
        background-color: #FAFAFA;
        border-bottom: 1px solid #E5E7EB;
        padding: 2px 4px;
        font-size: 13px;
        color: #374151;
    }
    QMenuBar::item {
        padding: 5px 12px;
        border-radius: 5px;
        background: transparent;
    }
    QMenuBar::item:selected {
        background-color: #EEF2FF;
        color: #2563EB;
    }
    QMenuBar::item:pressed {
        background-color: #E0EAFF;
    }
    QMenu {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 6px;
        font-size: 13px;
        color: #374151;
    }
    QMenu::item {
        padding: 7px 30px 7px 14px;
        border-radius: 5px;
    }
    QMenu::item:selected {
        background-color: #2563EB;
        color: #FFFFFF;
    }
    QMenu::item:disabled {
        color: #9CA3AF;
    }
    QMenu::separator {
        height: 1px;
        background: #E5E7EB;
        margin: 6px 8px;
    }
"""


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
            "theme": "light",
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

    def _make_action(self, text, shortcut=None, slot=None, checkable=False, checked=False):
        """统一的 QAction 工厂方法"""
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut))
        if slot:
            act.triggered.connect(slot)
        if checkable:
            act.setCheckable(True)
            act.setChecked(checked)
        return act

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet(MENU_QSS)

        # ── 1. 文件菜单 ──────────────────────────────
        file_menu = menu_bar.addMenu("文件(&F)")
        file_menu.addAction(self._make_action("📂 打开...", "Ctrl+O", self.open_file_dialog))
        file_menu.addAction(self._make_action("💾 保存", "Ctrl+S", self.save_file))
        file_menu.addAction(self._make_action("📥 另存为...", "Ctrl+Shift+S", self.save_file_as))
        file_menu.addSeparator()
        file_menu.addAction(self._make_action("📄 导出为 PDF...", None, self.export_to_pdf))
        file_menu.addSeparator()
        file_menu.addAction(self._make_action("🚪 退出", "Alt+F4", self.close))

        # ── 2. 编辑菜单 ──────────────────────────────
        edit_menu = menu_bar.addMenu("编辑(&E)")
        edit_menu.addAction(self._make_action("↩️ 撤销", "Ctrl+Z",
                             lambda: self.run_editor_command("undo")))
        edit_menu.addAction(self._make_action("↪️ 重做", "Ctrl+Y",
                             lambda: self.run_editor_command("redo")))
        edit_menu.addSeparator()
        edit_menu.addAction(self._make_action("✂️ 剪切", "Ctrl+X",
                             lambda: self.run_editor_command("cut")))
        edit_menu.addAction(self._make_action("📋 复制", "Ctrl+C",
                             lambda: self.run_editor_command("copy")))
        edit_menu.addAction(self._make_action("📌 粘贴", "Ctrl+V",
                             lambda: self.run_editor_command("paste")))
        edit_menu.addSeparator()
        edit_menu.addAction(self._make_action("🗑️ 全选", "Ctrl+A",
                             lambda: self.run_editor_command("selectAll")))

        # ── 3. 视图菜单 ──────────────────────────────
        view_menu = menu_bar.addMenu("视图(&V)")

        self.toggle_outline_act = self._make_action(
            "📋 左侧大纲栏", None, lambda chk: self.outline_widget.setVisible(chk),
            checkable=True, checked=True)
        view_menu.addAction(self.toggle_outline_act)

        self.toggle_ai_sidebar_act = self._make_action(
            "🤖 右侧 AI 侧边栏", None, lambda chk: self.ai_sidebar.setVisible(chk),
            checkable=True, checked=True)
        view_menu.addAction(self.toggle_ai_sidebar_act)

        view_menu.addSeparator()

        saved_theme = self.ai_config.get("theme", "light")
        self.light_theme_act = self._make_action(
            "☀️ 亮色主题", None, lambda: self.set_theme("light"),
            checkable=True, checked=(saved_theme != "dark"))
        view_menu.addAction(self.light_theme_act)

        self.dark_theme_act = self._make_action(
            "🌙 暗色主题", None, lambda: self.set_theme("dark"),
            checkable=True, checked=(saved_theme == "dark"))
        view_menu.addAction(self.dark_theme_act)

        # 主题互斥
        self.light_theme_act.toggled.connect(lambda on: self.dark_theme_act.setChecked(not on))
        self.dark_theme_act.toggled.connect(lambda on: self.light_theme_act.setChecked(not on))

        # ── 4. AI 助手菜单 ──────────────────────────
        ai_menu = menu_bar.addMenu("🤖 AI 助手(&A)")

        self.provider_info_act = QAction("🔌 当前服务：未配置", self)
        self.provider_info_act.setEnabled(False)
        ai_menu.addAction(self.provider_info_act)

        ai_menu.addSeparator()
        ai_menu.addAction(self._make_action("⚙️ 设置 API Key 与 模型服务...", None,
                           self.open_ai_config_dialog))

        ai_menu.addSeparator()
        ai_menu.addAction(self._make_action("🚀 生成全文摘要", None,
            lambda: self.quick_ai_action("请帮我总结当前文档的核心要点并生成全文摘要。")))
        ai_menu.addAction(self._make_action("💡 扩写与细节丰富", None,
            lambda: self.quick_ai_action("请对当前文档内容进行扩写，补充更多细节和逻辑支撑。")))
        ai_menu.addAction(self._make_action("✨ 文章润色与纠错", None,
            lambda: self.quick_ai_action("请纠正当前文档中的错别字与语法错误，并润色语句使其更流畅。")))

        # ── 5. 帮助菜单 ──────────────────────────────
        help_menu = menu_bar.addMenu("帮助(&H)")
        help_menu.addAction(self._make_action("ℹ️ 关于 SmartMarkdown", None, self.show_about))

        # 刷新服务商状态显示
        self.refresh_provider_display()

    def refresh_provider_display(self):
        """更新 AI 菜单中当前服务商的信息展示"""
        if hasattr(self, 'provider_info_act'):
            provider = self.ai_config.get("current_provider", "未配置")
            model = self.ai_config.get("model", "-")
            self.provider_info_act.setText(f"🔌 当前服务：{provider}（{model}）")

    def run_editor_command(self, command: str):
        """让 WebEngine 中的编辑器执行对应的原生编辑命令"""
        self.viewer.page().runJavaScript(f"document.execCommand('{command}');")

    def set_theme(self, theme: str):
        """切换亮/暗主题：动态调用页面 applyTheme() 注入全局主题 CSS，并持久化到配置。"""
        # 从 config 的统一主题表中取对应 CSS
        css = THEME_CSS.get(theme, THEME_CSS["light"]).strip()
        css_literal = json.dumps(css)
        self.viewer.page().runJavaScript(f"applyTheme({css_literal});")

        # 持久化，保证下次启动时 md_parser 用正确的初始主题
        self.ai_config["theme"] = theme
        self.save_ai_config()

        self.light_theme_act.setChecked(theme == "light")
        self.dark_theme_act.setChecked(theme == "dark")
        self.status_bar.showMessage(f"🎨 已切换至{'暗色' if theme == 'dark' else '亮色'}主题")

    def quick_ai_action(self, prompt: str):
        """通过菜单触发的 AI 快捷指令"""
        self.handle_ai_request(prompt, "rendered")

    def show_about(self):
        QMessageBox.about(
            self, "关于 SmartMarkdown",
            "<h3>🚀 SmartMarkdown</h3>"
            "<p>一款具备 <b>AI 辅助写作</b>、<b>LaTeX 数学公式</b> 与 "
            "<b>Mermaid 图表</b> 实时渲染的智能 Markdown 桌面编辑器。</p>"
            "<p>基于 PyQt6 + Vditor + 多模型 AI 服务实现。</p>"
            "<p style='color:#6B7280'>开源协议：MIT License</p>"
        )

    def save_file_as(self):
        """另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", self.current_file_path or "", "Markdown Files (*.md)"
        )
        if not file_path:
            return
        self.current_file_path = file_path
        FileManager.save_file(file_path, self.current_markdown_text)
        self.status_bar.showMessage(f"✅ 已保存: {file_path}")

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
        theme = self.ai_config.get("theme", "light")
        editor_html = MarkdownParserEngine.get_editor_html(demo_text, theme)
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

        if self.ai_thread is not None:
            # 复用已有的线程对象，避免重复创建/删除导致的对象生命周期问题
            self.ai_thread.finished_signal.disconnect(self.on_ai_success)
            self.ai_thread.error_signal.disconnect(self.on_ai_error)
            self.ai_thread.deleteLater()

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
        # 注意：不能用 self.ai_thread.finished.connect(self.ai_thread.deleteLater)，
        # 否则线程结束后再次请求删除已销毁的 QThread 对象，会导致闪退。
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
            self.refresh_provider_display()
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
