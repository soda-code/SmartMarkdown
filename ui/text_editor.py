# ui/text_editor.py
import os
import time
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QKeySequence

class CodeTextEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas", 11))
        self.setPlaceholderText("在此输入 Markdown 源码...")
        # padding 调整为 20px，文字靠左紧凑排版
        self.setStyleSheet("""
            QPlainTextEdit {
                border: none;
                padding: 20px 20px;
                background-color: #ffffff;
                font-family: 'Consolas', monospace;
                font-size: 15px;
                line-height: 1.6;
            }
        """)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            clipboard = self.get_clipboard_image()
            if clipboard:
                image_path = self.save_clipboard_image(clipboard)
                if image_path:
                    self.insertPlainText(f"\n![图片]({image_path})\n")
                    return
        super().keyPressEvent(event)

    def get_clipboard_image(self):
        from PyQt6.QtWidgets import QApplication
        cb = QApplication.clipboard()
        mime_data = cb.mimeData()
        if mime_data.hasImage():
            return cb.image()
        return None

    def save_clipboard_image(self, qimage) -> str:
        img_dir = os.path.join(os.getcwd(), "images")
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            
        filename = f"img_{int(time.time())}.png"
        file_path = os.path.join(img_dir, filename)
        qimage.save(file_path, "PNG")
        return f"./images/{filename}"