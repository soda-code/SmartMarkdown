# file_manager.py
import re

class FileManager:
    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def save_file(file_path: str, content: str) -> bool:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    @staticmethod
    def calculate_stats(text: str) -> tuple:
        clean_text = re.sub(r'[^\w\u4e00-\u9fa5]', '', text)
        char_count = len(clean_text)
        word_count = len(text.split())
        read_time = max(1, round(char_count / 300)) if char_count > 0 else 0
        return char_count, word_count, read_time