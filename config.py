# config.py

APP_NAME = "SmartMarkdown"

# 亮色主题：margin: 0 (靠左对齐), padding: 25px 25px (紧凑布局)
GITHUB_TYPORA_CSS = """
<style>
    html { scroll-behavior: smooth; }
    body {
        font-family: "Open Sans", "Clear Sans", "Helvetica Neue", Helvetica, Arial, "Microsoft YaHei", sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #333333;
        max-width: 900px;
        margin: 0;
        padding: 25px 25px;
        background-color: #ffffff;
    }
    h1, h2, h3, h4, h5, h6 { color: #333333; font-weight: bold; margin-top: 1.5em; margin-bottom: 0.8em; }
    h1 { font-size: 2.25em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
    h2 { font-size: 1.75em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 14px; }
    th, td { border: 1px solid #dcdcdc; padding: 8px 12px; text-align: left; }
    th { background-color: #f8f8f8; font-weight: bold; }
    tr:nth-child(even) { background-color: #fbfbfb; }
    code { background-color: #f3f4f4; color: #c7254e; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }
    pre { background-color: #f8f8f8; border: 1px solid #e7e7e7; border-radius: 5px; padding: 12px 16px; overflow: auto; }
    pre code { background-color: transparent; color: inherit; padding: 0; }
    blockquote { border-left: 4px solid #dfe2e5; color: #777777; padding: 0 15px; margin: 15px 0; }
    img { max-width: 100%; height: auto; border-radius: 4px; }
</style>
"""

# 夜间主题：靠左对齐
NIGHT_TYPORA_CSS = """
<style>
    html { scroll-behavior: smooth; }
    body {
        font-family: "Open Sans", "Microsoft YaHei", sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: #b2b2b2;
        max-width: 900px;
        margin: 0;
        padding: 25px 25px;
        background-color: #36393e;
    }
    h1, h2, h3, h4, h5 { color: #e6e6e6; font-weight: bold; margin-top: 1.5em; margin-bottom: 0.8em; }
    h1 { font-size: 2.25em; border-bottom: 1px solid #484b51; padding-bottom: 0.3em; }
    h2 { font-size: 1.75em; border-bottom: 1px solid #484b51; padding-bottom: 0.3em; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 14px; }
    th, td { border: 1px solid #484b51; padding: 8px 12px; }
    th { background-color: #2e3136; color: #e6e6e6; }
    tr:nth-child(even) { background-color: #2e3136; }
    code { background-color: #282b30; color: #e28743; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }
    pre { background-color: #1e2124; border: 1px solid #282b30; border-radius: 5px; padding: 12px 16px; overflow: auto; }
    pre code { background-color: transparent; color: inherit; }
    blockquote { border-left: 4px solid #7289da; color: #8a8e94; padding: 0 15px; margin: 15px 0; }
    img { max-width: 100%; height: auto; border-radius: 4px; }
</style>
"""

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