# config.py

APP_NAME = "SmartMarkdown"

EXTENDED_SCRIPTS = """
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  },
  svg: { fontCache: 'global' }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function() {
    mermaid.initialize({ startOnLoad: true, theme: 'default' });
  });
</script>
"""

# ── 全局主题 CSS（内联进 Vditor HTML，使切换彻底、全局、持久生效） ──────────
# 注意：定义时不含 <style> 包裹，方便在 HTML 模板与 JS 动态注入中复用。
LIGHT_THEME_CSS = """
html, body, .vditor {
    background-color: #ffffff !important;
    color: #333333 !important;
}
.vditor {
    background-color: #ffffff !important;
}
.vditor-content {
    background-color: #ffffff !important;
}
.vditor-tx, .vditor-reset, .vditor-ir,
.vditor-tx > div, .vditor-wysiwyg {
    background-color: #ffffff !important;
    color: #333333 !important;
    caret-color: #333333 !important;
}
.vditor-toolbar {
    background-color: #fafafa !important;
    border-bottom: 1px solid #e5e7eb !important;
}
.vditor-toolbar .vditor-icon svg {
    fill: #4b5563 !important;
}
.vditor-toolbar button:hover,
.vditor-toolbar button.vditor-menu--current,
.vditor-toolbar .vditor-menu--current {
    background-color: #f3f4f6 !important;
    color: #2563eb !important;
}
.vditor-tx h1, .vditor-tx h2, .vditor-tx h3,
.vditor-tx h4, .vditor-tx h5, .vditor-tx h6,
.vditor-reset h1, .vditor-reset h2, .vditor-reset h3,
.vditor-reset h4, .vditor-reset h5, .vditor-reset h6 {
    color: #333333 !important;
    border-bottom-color: #eeeeee !important;
}
.vditor-tx p, .vditor-tx li, .vditor-tx td, .vditor-tx th,
.vditor-tx span, .vditor-tx div,
.vditor-reset p, .vditor-reset li, .vditor-reset td, .vditor-reset th {
    color: #333333 !important;
}
.vditor-tx a, .vditor-reset a { color: #2563eb !important; }
.vditor-tx blockquote, .vditor-reset blockquote {
    border-left: 4px solid #dfe2e5 !important;
    color: #777777 !important;
    background-color: #fafafa !important;
}
.vditor-tx code, .vditor-reset code {
    background-color: #f3f4f6 !important;
    color: #c7254e !important;
}
.vditor-tx pre, .vditor-reset pre {
    background-color: #f8f8f8 !important;
    border: 1px solid #e7e7e7 !important;
}
.vditor-tx pre code, .vditor-reset pre code {
    background-color: transparent !important;
    color: #333333 !important;
}
.vditor-tx table, .vditor-reset table { border-color: #dcdcdc !important; }
.vditor-tx th, .vditor-tx td,
.vditor-reset th, .vditor-reset td { border-color: #dcdcdc !important; }
.vditor-tx th, .vditor-reset th { background-color: #f8f8f8 !important; color: #333333 !important; }
.vditor-tx tr:nth-child(even), .vditor-reset tr:nth-child(even) { background-color: #fbfbfb !important; }
.vditor-tx hr, .vditor-reset hr { background-color: #e5e7eb !important; }
.vditor-tx img, .vditor-reset img { border-radius: 4px !important; }
"""

# 夜间主题
DARK_THEME_CSS = """
html, body, .vditor {
    background-color: #36393e !important;
    color: #b2b2b2 !important;
}
.vditor {
    background-color: #36393e !important;
}
.vditor-content {
    background-color: #36393e !important;
}
.vditor-tx, .vditor-reset, .vditor-ir,
.vditor-tx > div, .vditor-wysiwyg {
    background-color: #36393e !important;
    color: #b2b2b2 !important;
    caret-color: #b2b2b2 !important;
}
.vditor-toolbar {
    background-color: #2e3136 !important;
    border-bottom: 1px solid #484b51 !important;
}
.vditor-toolbar .vditor-icon svg {
    fill: #b2b2b2 !important;
}
.vditor-toolbar button:hover,
.vditor-toolbar button.vditor-menu--current,
.vditor-toolbar .vditor-menu--current {
    background-color: #40444b !important;
    color: #ffffff !important;
}
.vditor-tx h1, .vditor-tx h2, .vditor-tx h3,
.vditor-tx h4, .vditor-tx h5, .vditor-tx h6,
.vditor-reset h1, .vditor-reset h2, .vditor-reset h3,
.vditor-reset h4, .vditor-reset h5, .vditor-reset h6 {
    color: #e6e6e6 !important;
    border-bottom-color: #484b51 !important;
}
.vditor-tx p, .vditor-tx li, .vditor-tx td, .vditor-tx th,
.vditor-tx span, .vditor-tx div,
.vditor-reset p, .vditor-reset li, .vditor-reset td, .vditor-reset th {
    color: #b2b2b2 !important;
}
.vditor-tx a, .vditor-reset a { color: #7aa2f7 !important; }
.vditor-tx blockquote, .vditor-reset blockquote {
    border-left: 4px solid #7289da !important;
    color: #8a8e94 !important;
    background-color: #2e3136 !important;
}
.vditor-tx code, .vditor-reset code {
    background-color: #282b30 !important;
    color: #e28743 !important;
}
.vditor-tx pre, .vditor-reset pre {
    background-color: #1e2124 !important;
    border: 1px solid #282b30 !important;
}
.vditor-tx pre code, .vditor-reset pre code {
    background-color: transparent !important;
    color: #b2b2b2 !important;
}
.vditor-tx table, .vditor-reset table { border-color: #484b51 !important; }
.vditor-tx th, .vditor-tx td,
.vditor-reset th, .vditor-reset td { border-color: #484b51 !important; }
.vditor-tx th, .vditor-reset th { background-color: #2e3136 !important; color: #e6e6e6 !important; }
.vditor-tx tr:nth-child(even), .vditor-reset tr:nth-child(even) { background-color: #2e3136 !important; }
.vditor-tx hr, .vditor-reset hr { background-color: #484b51 !important; }
.vditor-tx img, .vditor-reset img { border-radius: 4px !important; }
"""

THEME_CSS = {
    "light": LIGHT_THEME_CSS,
    "dark": DARK_THEME_CSS,
}

# 编辑器加载占位指示（解决 CDN 加载慢导致的“白屏/无提示”问题）
LOADING_PLACEHOLDER = """
<div id="sm-loading" style="
    position: fixed; inset: 0; z-index: 9999;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background-color: #ffffff; color: #6B7280;
    font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif; font-size: 14px;
">
    <div class="sm-spinner" style="
        width: 34px; height: 34px; margin-bottom: 14px;
        border: 3px solid #e5e7eb; border-top-color: #2563eb;
        border-radius: 50%; animation: sm-spin 0.9s linear infinite;
    "></div>
    <div>🚀 正在加载 Editor...</div>
    <style>@keyframes sm-spin { to { transform: rotate(360deg); } }</style>
</div>
"""

# 用于在 JS 中调用时同时保留加载层；编辑器 after 回调后移除
HIDE_LOADING_JS = "var l=document.getElementById('sm-loading');if(l)l.parentNode.removeChild(l);"
