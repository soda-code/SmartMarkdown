import json

class MarkdownParserEngine:
    @staticmethod
    def get_editor_html(initial_content: str = "") -> str:
        """
        生成纯粹的 WYSIWYG 所见即所得编辑 HTML 模板。
        取消了模式切换，强化了悬停矩形框提示 (Tooltip) 与高可靠通信。
        """
        json_content = json.dumps(initial_content)
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartMarkdown Editor</title>
    <!-- 使用高可用 CDN 节点 -->
    <link rel="stylesheet" href="https://unpkg.com/vditor@3.9.9/dist/index.css"/>
    <script src="https://unpkg.com/vditor@3.9.9/dist/index.min.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        body, html {{ 
            margin: 0; padding: 0; height: 100%; width: 100%; 
            overflow: hidden; background-color: #ffffff;
        }}
        #vditor {{ height: 100vh !important; border: none !important; }}
        .vditor-toolbar {{ 
            border-bottom: 1px solid #E5E7EB !important; 
            background-color: #FAFAFA !important; 
        }}
        /* 强效美化 Tooltip 矩形提示框样式 */
        .vditor-tooltipped::after {{
            background-color: #1F2937 !important;
            color: #F9FAFB !important;
            font-size: 12px !important;
            padding: 5px 9px !important;
            border-radius: 4px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }}
    </style>
</head>
<body>
    <div id="vditor"></div>
    <script>
        var pyBridge = null;
        var vditorEditor = null;
        var isEditorReady = false;

        // 1. 初始化 Qt 双向通信通道
        if (typeof qt !== 'undefined') {{
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                pyBridge = channel.objects.pyBridge;
            }});
        }}

        // 2. 初始化纯所见即所得编辑器
        vditorEditor = new Vditor('vditor', {{
            mode: 'wysiwyg',
            height: '100vh',
            value: {json_content},
            cache: {{ enable: false }},
            toolbarConfig: {{ hide: false, pin: true }},
            preview: {{
                math: {{ engine: 'MathJax' }},
                hljs: {{ enable: true, style: 'github' }},
                markdown: {{ toc: true }}
            }},
            after: function() {{
                isEditorReady = true;
            }},
            // 配置全套带 Tooltip 悬停框功能的工具栏
            toolbar: [
                {{ name: 'emoji', tip: '插入 Emoji 表情' }},
                {{ name: 'headings', tip: '设置标题级别 (H1~H6)' }},
                {{ name: 'bold', tip: '文本加粗 (Ctrl+B)' }},
                {{ name: 'italic', tip: '文本斜体 (Ctrl+I)' }},
                {{ name: 'strike', tip: '添加删除线' }},
                {{ name: 'link', tip: '插入超链接' }},
                '|',
                {{ name: 'list', tip: '无序列表' }},
                {{ name: 'ordered-list', tip: '有序列表' }},
                {{ name: 'check', tip: '任务列表 (Todo)' }},
                '|',
                {{ name: 'quote', tip: '引用区块' }},
                {{ name: 'line', tip: '添加水平分割线' }},
                {{ name: 'code', tip: '插入多行代码块' }},
                {{ name: 'inline-code', tip: '行内代码' }},
                '|',
                {{ name: 'table', tip: '插入 Markdown 表格' }},
                {{ name: 'insert-before', tip: '在上方插入块' }},
                {{ name: 'insert-after', tip: '在下方插入块' }},
                '|',
                {{ name: 'undo', tip: '撤销 (Ctrl+Z)' }},
                {{ name: 'redo', tip: '重做 (Ctrl+Y)' }},
                '|',
                {{ name: 'outline', tip: '展开或隐藏文档大纲' }}
            ],
            input: function(value) {{
                if (pyBridge) {{
                    pyBridge.on_text_changed_from_web(value);
                }}
            }}
        }});

        // 3. 供 Python 强力刷新的稳定接口
        function setMarkdownContent(content) {{
            if (vditorEditor && isEditorReady) {{
                vditorEditor.setValue(content);
            }}
        }}

        function insertMarkdownContent(text) {{
            if (vditorEditor && isEditorReady) {{
                vditorEditor.insertValue(text);
            }}
        }}
    </script>
</body>
</html>
"""