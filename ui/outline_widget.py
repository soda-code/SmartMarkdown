# ui/outline_widget.py
import re
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

class OutlineWidget(QTreeWidget):
    heading_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("大纲")
        self.setFont(QFont("Microsoft YaHei", 9))
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #fafafa;
                border: none;
                border-right: 1px solid #e8e8e8;
            }
            QTreeWidget::item { padding: 6px 10px; color: #555; }
            QTreeWidget::item:hover { background-color: #f0f0f0; }
            QTreeWidget::item:selected { background-color: #e6f7ff; color: #1890ff; font-weight: bold; }
        """)
        self.itemClicked.connect(self.on_item_clicked)

    def update_outline(self, raw_md_text: str):
        self.clear()
        lines = raw_md_text.split('\n')
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        root_item = self.invisibleRootItem()
        last_items = {0: root_item}
        
        header_index = 0
        for line in lines:
            match = heading_pattern.match(line.strip())
            if match:
                header_index += 1
                level = len(match.group(1))
                title = match.group(2).strip()

                item = QTreeWidgetItem([title])
                item.setData(0, 32, header_index)
                
                parent_level = level - 1
                while parent_level > 0 and parent_level not in last_items:
                    parent_level -= 1
                
                parent_node = last_items.get(parent_level, root_item)
                parent_node.addChild(item)
                last_items[level] = item
                
        self.expandAll()

    def on_item_clicked(self, item, column):
        header_idx = item.data(0, 32)
        if header_idx:
            self.heading_clicked.emit(header_idx)