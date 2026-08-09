# md_parser.py
import markdown
import re
from config import GITHUB_TYPORA_CSS, NIGHT_TYPORA_CSS, EXTENDED_SCRIPTS

class MarkdownParserEngine:
    def __init__(self):
        self.extensions = [
            'tables', 'fenced_code', 'codehilite', 'nl2br', 'toc', 'pymdownx.arithmatex'
        ]
        self.extension_configs = {
            'pymdownx.arithmatex': { 'generic': True }
        }
        self.current_theme = "light"

    def parse(self, raw_md_text: str) -> str:
        try:
            processed_text = self._preprocess_mermaid(raw_md_text)

            md = markdown.Markdown(
                extensions=self.extensions, 
                extension_configs=self.extension_configs
            )
            body_html = md.convert(processed_text)
            body_html = self._add_header_ids(body_html)

            css = NIGHT_TYPORA_CSS if self.current_theme == "dark" else GITHUB_TYPORA_CSS
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                {css}
                {EXTENDED_SCRIPTS}
            </head>
            <body>
                {body_html}
            </body>
            </html>
            """
            return full_html
        except Exception as e:
            return f"<html><body><h3 style='color:red;'>解析错误: {str(e)}</h3></body></html>"

    def _preprocess_mermaid(self, text: str) -> str:
        pattern = r'```mermaid\s*\n(.*?)\n```'
        replacement = r'<div class="mermaid">\1</div>'
        return re.sub(pattern, replacement, text, flags=re.DOTALL)

    def _add_header_ids(self, html: str) -> str:
        idx = 0
        def replacer(match):
            nonlocal idx
            idx += 1
            tag = match.group(1)
            content = match.group(2)
            return f'<{tag} id="heading-{idx}">{content}</{tag}>'
        
        pattern = r'<(h[1-6])>(.*?)</\1>'
        return re.sub(pattern, replacer, html)

    def set_theme(self, theme_name: str):
        self.current_theme = theme_name