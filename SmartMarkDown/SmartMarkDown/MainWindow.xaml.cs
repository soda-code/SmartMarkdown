using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using Microsoft.Win32;
using Markdig;

namespace SmartMarkDown
{
    public partial class MainWindow : Window
    {
        private readonly MarkdownPipeline _pipeline;
        private readonly AiService _aiService = new AiService();
        private string _currentFilePath = string.Empty;
        private bool _isModified = false;
        private bool _isDarkMode = false;
        private bool _isReaderOnly = false;
        private bool _isInitializing = false;

        public MainWindow()
        {
            InitializeComponent();

            // 启用 Markdig 高级扩展、数学公式扩展与 Emoji
            _pipeline = new MarkdownPipelineBuilder()
                .UseAdvancedExtensions()
                .UseMathematics()
                .UseEmojiAndSmiley()
                .Build();

            CmbModels.ItemsSource = _aiService.Providers;
            CmbModels.SelectedIndex = 0;

            KeyDown += MainWindow_KeyDown;
            InitializeWebView();
        }

        private async void InitializeWebView()
        {
            await BrowserPreview.EnsureCoreWebView2Async();
            NewDocument(promptSave: false);
        }

        private void MainWindow_KeyDown(object sender, KeyEventArgs e)
        {
            if (Keyboard.Modifiers == ModifierKeys.Control)
            {
                if (e.Key == Key.N)
                {
                    BtnNew_Click(null, null);
                    e.Handled = true;
                }
                else if (e.Key == Key.O)
                {
                    BtnOpen_Click(null, null);
                    e.Handled = true;
                }
                else if (e.Key == Key.S)
                {
                    BtnSave_Click(null, null);
                    e.Handled = true;
                }
            }
        }

        private void UpdateWindowTitle()
        {
            string fileName = string.IsNullOrEmpty(_currentFilePath) ? "Untitled-1" : Path.GetFileName(_currentFilePath);
            string mod = _isModified ? " •" : "";
            Title = $"{fileName}{mod} - SmartMarkDown";
        }

        private void UpdatePreview()
        {
            if (BrowserPreview?.CoreWebView2 == null) return;

            string rawHtml = Markdown.ToHtml(TxtMarkdown.Text ?? string.Empty, _pipeline);

            string themeName = _isDarkMode ? "dark" : "default";
            string cssTheme = _isDarkMode
                ? "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css"
                : "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.min.css";

            string bgColor = _isDarkMode ? "#1E1E1E" : "#FFFFFF";
            string textColor = _isDarkMode ? "#D4D4D4" : "#333333";
            string tableBgEven = _isDarkMode ? "#252526" : "#F6F8FA";
            string tableBorder = _isDarkMode ? "#3C3C3C" : "#D0D7DE";
            string scrollThumb = _isDarkMode ? "#424242" : "#C1C1C1";

            string fullHtml = $@"
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset='utf-8'/>
                <link rel='stylesheet' href='{cssTheme}'>
                <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css'>
                <script defer src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js'></script>
                <script defer src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js'></script>
                <script src='https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.0/mermaid.min.js'></script>
                <style>
                    ::-webkit-scrollbar {{
                        width: 8px;
                        height: 8px;
                    }}
                    ::-webkit-scrollbar-track {{
                        background: transparent;
                    }}
                    ::-webkit-scrollbar-thumb {{
                        background: {scrollThumb};
                        border-radius: 4px;
                    }}
                    ::-webkit-scrollbar-thumb:hover {{
                        background: #686868;
                    }}

                    body {{
                        background-color: {bgColor} !important;
                        color: {textColor} !important;
                        box-sizing: border-box;
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 24px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Consolas', sans-serif;
                    }}
                    .markdown-body {{
                        background-color: transparent !important;
                        color: {textColor} !important;
                    }}
                    .markdown-body table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 16px 0;
                        display: table !important;
                    }}
                    .markdown-body table th, .markdown-body table td {{
                        border: 1px solid {tableBorder} !important;
                        padding: 8px 14px;
                    }}
                    .markdown-body table tr:nth-child(2n) {{
                        background-color: {tableBgEven} !important;
                    }}
                    .markdown-body pre {{
                        background-color: {(_isDarkMode ? "#252526" : "#F6F8FA")} !important;
                        border: 1px solid {tableBorder};
                        border-radius: 6px;
                    }}
                    .mermaid {{
                        background: transparent;
                        text-align: center;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body class='markdown-body'>
                {rawHtml}
                <script>
                    document.querySelectorAll('pre code.language-mermaid').forEach(function(block) {{
                        var pre = block.parentElement;
                        var div = document.createElement('div');
                        div.className = 'mermaid';
                        div.textContent = block.textContent;
                        pre.parentNode.replaceChild(div, pre);
                    }});

                    try {{
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: '{themeName}',
                            securityLevel: 'loose'
                        }});
                        mermaid.run();
                    }} catch(e) {{}}

                    document.addEventListener('DOMContentLoaded', function() {{
                        if (typeof renderMathInElement !== 'undefined') {{
                            renderMathInElement(document.body, {{
                                delimiters: [
                                    {{left: '$$', right: '$$', display: true}},
                                    {{left: '$', right: '$', display: false}},
                                    {{left: '\\[', right: '\\]', display: true}},
                                    {{left: '\\(', right: '\\)', display: false}}
                                ],
                                throwOnError: false
                            }});
                        }}
                    }});
                </script>
            </body>
            </html>";

            BrowserPreview.NavigateToString(fullHtml);
        }

        private void TxtMarkdown_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (!_isInitializing)
            {
                _isModified = true;
                UpdateWindowTitle();
            }

            UpdatePreview();

            string text = TxtMarkdown.Text ?? string.Empty;
            int charCount = text.Length;
            int wordCount = Regex.Matches(text, @"[\w\u4e00-\u9fa5]+").Count;
            StatusWordCount.Text = $"{charCount} 字符 | {wordCount} 词";
        }

        #region 文件管理

        private bool PromptSaveIfModified()
        {
            if (!_isModified) return true;

            string docName = string.IsNullOrEmpty(_currentFilePath) ? "未命名文档" : Path.GetFileName(_currentFilePath);
            var result = MessageBox.Show($"是否将更改保存到 \"{docName}\"？", "SmartMarkDown", MessageBoxButton.YesNoCancel, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                return PerformSave();
            }
            if (result == MessageBoxResult.No)
            {
                return true;
            }

            return false;
        }

        private bool PerformSave()
        {
            if (string.IsNullOrEmpty(_currentFilePath))
            {
                var dlg = new SaveFileDialog { Filter = "Markdown 文件 (*.md)|*.md|所有文件 (*.*)|*.*", FileName = "Untitled.md" };
                if (dlg.ShowDialog() == true)
                {
                    _currentFilePath = dlg.FileName;
                }
                else
                {
                    return false;
                }
            }

            File.WriteAllText(_currentFilePath, TxtMarkdown.Text);
            _isModified = false;
            UpdateWindowTitle();
            StatusMessage.Text = "文件已保存";
            return true;
        }

        private void NewDocument(bool promptSave = true)
        {
            if (promptSave && !PromptSaveIfModified()) return;

            _isInitializing = true;
            _currentFilePath = string.Empty;

            var sb = new StringBuilder();
            sb.AppendLine("# 🚀 Markdown 现代创作空间");
            sb.AppendLine();
            sb.AppendLine("## 1. 流程图与时序图 (Mermaid)");
            sb.AppendLine();
            sb.AppendLine("```mermaid");
            sb.AppendLine("graph TD");
            sb.AppendLine("    A[用户编写 Markdown] --> B[Markdig 语法解析]");
            sb.AppendLine("    B --> C{是否包含公式/图表?}");
            sb.AppendLine("    C -->|包含图表| D[Mermaid 矢量渲染]");
            sb.AppendLine("    C -->|包含公式| E[KaTeX 引擎排版]");
            sb.AppendLine("    D --> F[WebView2 现代化呈现]");
            sb.AppendLine("    E --> F");
            sb.AppendLine("```");
            sb.AppendLine();
            sb.AppendLine("## 2. 现代表格 (GFM Table)");
            sb.AppendLine();
            sb.AppendLine("| 功能模块 | 支持标准 | 渲染状态 |");
            sb.AppendLine("| :--- | :--- | :---: |");
            sb.AppendLine("| 基础排版 | CommonMark / GFM | ✅ 极速渲染 |");
            sb.AppendLine("| 流程图 | Mermaid v10+ | ✅ 完美支持 |");
            sb.AppendLine("| 数学公式 | LaTeX / KaTeX | ✅ 高精度排版 |");
            sb.AppendLine();
            sb.AppendLine("## 3. 数学公式 (KaTeX)");
            sb.AppendLine();
            sb.AppendLine("行内公式质能方程：$E = mc^2$，欧拉公式：$e^{i\\pi} + 1 = 0$");
            sb.AppendLine();
            sb.AppendLine("独立块级高斯积分公式：");
            sb.AppendLine();
            sb.AppendLine("$$\\int_{-\\infty}^{+\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$");
            sb.AppendLine();

            TxtMarkdown.Text = sb.ToString();
            _isModified = false;
            _isInitializing = false;

            UpdateWindowTitle();
            StatusMessage.Text = "新建文件就绪";
        }

        private void BtnNew_Click(object sender, RoutedEventArgs e) => NewDocument(promptSave: true);

        private void BtnOpen_Click(object sender, RoutedEventArgs e)
        {
            if (!PromptSaveIfModified()) return;

            var dlg = new OpenFileDialog { Filter = "Markdown 文件 (*.md;*.markdown)|*.md;*.markdown|所有文件 (*.*)|*.*" };
            if (dlg.ShowDialog() == true)
            {
                _isInitializing = true;
                _currentFilePath = dlg.FileName;
                TxtMarkdown.Text = File.ReadAllText(_currentFilePath);
                _isModified = false;
                _isInitializing = false;

                UpdateWindowTitle();
                StatusMessage.Text = $"已打开: {Path.GetFileName(_currentFilePath)}";
            }
        }

        private void BtnSave_Click(object sender, RoutedEventArgs e) => PerformSave();

        private void BtnSaveAs_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new SaveFileDialog { Filter = "Markdown 文件 (*.md)|*.md|所有文件 (*.*)|*.*", FileName = "Untitled.md" };
            if (dlg.ShowDialog() == true)
            {
                _currentFilePath = dlg.FileName;
                File.WriteAllText(_currentFilePath, TxtMarkdown.Text);
                _isModified = false;
                UpdateWindowTitle();
                StatusMessage.Text = "文件已另存为";
            }
        }

        private void BtnExportHtml_Click(object sender, RoutedEventArgs e)
        {
            var dlg = new SaveFileDialog { Filter = "HTML 文件 (*.html)|*.html", FileName = "Document.html" };
            if (dlg.ShowDialog() == true)
            {
                string body = Markdown.ToHtml(TxtMarkdown.Text ?? string.Empty, _pipeline);
                string doc = $"<!DOCTYPE html><html><head><meta charset='utf-8'/><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css'><link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css'></head><body class='markdown-body' style='padding:40px;max-width:850px;margin:auto;'>{body}</body></html>";
                File.WriteAllText(dlg.FileName, doc);
                StatusMessage.Text = "已导出为独立 HTML";
            }
        }

        #endregion

        #region 主题切换

        private void BtnToggleTheme_Click(object sender, RoutedEventArgs e)
        {
            _isDarkMode = !_isDarkMode;
            BtnThemeToggle.Content = _isDarkMode ? "☀️" : "🌙";
            MenuDarkMode.IsChecked = _isDarkMode;

            if (_isDarkMode)
            {
                Resources["BgBrush"] = new SolidColorBrush(Color.FromRgb(0x1E, 0x1E, 0x1E));
                Resources["CardBrush"] = new SolidColorBrush(Color.FromRgb(0x25, 0x25, 0x26));
                Resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(0x3C, 0x3C, 0x3C));
                Resources["TextPrimary"] = new SolidColorBrush(Color.FromRgb(0xD4, 0xD4, 0xD4));
                Resources["TextMuted"] = new SolidColorBrush(Color.FromRgb(0x85, 0x85, 0x85));
                Resources["ControlBg"] = new SolidColorBrush(Color.FromRgb(0x33, 0x33, 0x33));
                Resources["ControlHover"] = new SolidColorBrush(Color.FromRgb(0x44, 0x44, 0x44));

                Resources["MenuPopupBg"] = new SolidColorBrush(Color.FromRgb(0x25, 0x25, 0x26));
                Resources["MenuPopupBorder"] = new SolidColorBrush(Color.FromRgb(0x45, 0x45, 0x45));
                Resources["MenuHighlight"] = new SolidColorBrush(Color.FromRgb(0x09, 0x47, 0x71));

                Resources["StatusBarBg"] = new SolidColorBrush(Color.FromRgb(0x00, 0x7A, 0xCC));
                Resources["StatusBarFg"] = new SolidColorBrush(Colors.White);
            }
            else
            {
                Resources["BgBrush"] = new SolidColorBrush(Color.FromRgb(0xFF, 0xFF, 0xFF));
                Resources["CardBrush"] = new SolidColorBrush(Color.FromRgb(0xF3, 0xF3, 0xF3));
                Resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(0xE5, 0xE5, 0xE5));
                Resources["TextPrimary"] = new SolidColorBrush(Color.FromRgb(0x33, 0x33, 0x33));
                Resources["TextMuted"] = new SolidColorBrush(Color.FromRgb(0x71, 0x71, 0x71));
                Resources["ControlBg"] = new SolidColorBrush(Color.FromRgb(0xF8, 0xF8, 0xF8));
                Resources["ControlHover"] = new SolidColorBrush(Color.FromRgb(0xE8, 0xE8, 0xE8));

                Resources["MenuPopupBg"] = new SolidColorBrush(Color.FromRgb(0xFF, 0xFF, 0xFF));
                Resources["MenuPopupBorder"] = new SolidColorBrush(Color.FromRgb(0xCC, 0xCC, 0xCC));
                Resources["MenuHighlight"] = new SolidColorBrush(Color.FromRgb(0xE8, 0xE8, 0xE8));

                Resources["StatusBarBg"] = new SolidColorBrush(Color.FromRgb(0x00, 0x7A, 0xCC));
                Resources["StatusBarFg"] = new SolidColorBrush(Colors.White);
            }

            UpdatePreview();
        }

        #endregion

        #region AI 任务调度

        private void CmbModels_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (CmbModels.SelectedItem is AiProvider selected)
            {
                _aiService.CurrentProvider = selected;
                StatusCurrentModel.Text = $"模型: {selected.Name}";
            }
        }

        private void BtnConfigKey_Click(object sender, RoutedEventArgs e)
        {
            var provider = _aiService.CurrentProvider;
            if (provider == null) return;

            string key = Microsoft.VisualBasic.Interaction.InputBox(
                $"配置 [{provider.Name}] 的 API Key:\n端点: {provider.Endpoint}\n模型ID: {provider.ModelId}",
                "模型参数与密钥配置",
                provider.ApiKey
            );

            if (!string.IsNullOrEmpty(key))
            {
                provider.ApiKey = key.Trim();
                StatusMessage.Text = $"{provider.Name} 密钥已更新";
            }
        }

        private async Task RunAiCommandAsync(string prompt, bool replaceSelection = false, bool append = false)
        {
            string selection = TxtMarkdown.SelectedText;
            bool hasSelection = !string.IsNullOrWhiteSpace(selection);
            string targetText = hasSelection ? selection : TxtMarkdown.Text;

            if (string.IsNullOrWhiteSpace(targetText))
            {
                MessageBox.Show("请先输入或选择要处理的内容！", "提示", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            try
            {
                PanelAiLoading.Visibility = Visibility.Visible;
                StatusMessage.Text = $"正在请求 {_aiService.CurrentProvider.Name}...";

                string result = await _aiService.ProcessAsync(prompt, targetText);

                if (append)
                {
                    TxtMarkdown.AppendText("\n\n" + result);
                }
                else if (replaceSelection && hasSelection)
                {
                    TxtMarkdown.SelectedText = result;
                }
                else
                {
                    TxtMarkdown.Text = result;
                }

                StatusMessage.Text = "AI 生成完成";
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "AI 处理失败", MessageBoxButton.OK, MessageBoxImage.Warning);
                StatusMessage.Text = "AI 执行出错";
            }
            finally
            {
                PanelAiLoading.Visibility = Visibility.Collapsed;
            }
        }

        private async void AiPolish_Click(object sender, RoutedEventArgs e) =>
            await RunAiCommandAsync("你是一名专业文档编辑。请对以下 Markdown 文本进行错别字修正与语句润色，严格保留原有 Markdown 格式与代码块，直接输出润色后的结果：", replaceSelection: true);

        private async void AiSummarize_Click(object sender, RoutedEventArgs e) =>
            await RunAiCommandAsync("请为以下内容提取 3-5 条核心要点摘要，使用 Markdown 引用块（> ）格式输出：", append: true);

        private async void AiContinue_Click(object sender, RoutedEventArgs e) =>
            await RunAiCommandAsync("请根据前文上下文，逻辑顺畅地向后续写一段内容，保持一致的语气和 Markdown 排版格式：", append: true);

        private async void AiTranslate_Click(object sender, RoutedEventArgs e) =>
            await RunAiCommandAsync("请将以下内容翻译为准确地道的英文，保留所有 Markdown 格式与代码块不变：", replaceSelection: true);

        #endregion

        #region 编辑格式与快捷插入

        private void BtnToggleView_Click(object sender, RoutedEventArgs e)
        {
            _isReaderOnly = !_isReaderOnly;
            ColEditor.Width = _isReaderOnly ? new GridLength(0) : new GridLength(1, GridUnitType.Star);
            ColSplitter.Width = _isReaderOnly ? new GridLength(0) : new GridLength(4);
            BtnToggleView.Content = _isReaderOnly ? "✏️ 双栏编辑" : "👁️ 纯阅读";
            MenuOnlyPreview.IsChecked = _isReaderOnly;
        }

        private void ToolInsertBold_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"**{TxtMarkdown.SelectedText}**";
        private void ToolInsertItalic_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"*{TxtMarkdown.SelectedText}*";
        private void ToolInsertH2_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"\n## {TxtMarkdown.SelectedText}\n";
        private void ToolInsertCode_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"\n```csharp\n{TxtMarkdown.SelectedText}\n```\n";
        private void ToolInsertTable_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = "\n| 标题 1 | 标题 2 | 标题 3 |\n| :--- | :---: | ---: |\n| 靠左 | 居中 | 靠右 |\n";
        private void ToolInsertMermaid_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = "\n```mermaid\ngraph TD\n    A[开始] --> B(处理中)\n    B --> C{是否成功?}\n    C -->|是| D[结束]\n    C -->|否| B\n```\n";
        private void ToolInsertMath_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = "\n$$\nf(x) = \\int_{-\\infty}^x e^{-t^2} dt\n$$\n";
        private void ToolInsertLink_Click(object sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"[{TxtMarkdown.SelectedText}](https://example.com)";
        private void ToolClear_Click(object sender, RoutedEventArgs e) => TxtMarkdown.Clear();
        private void MenuExit_Click(object sender, RoutedEventArgs e) => Application.Current.Shutdown();

        #endregion
    }
}