using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Web;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using Microsoft.Win32;
using Markdig;
using Microsoft.Web.WebView2.Core;

namespace SmartMarkDown
{
    public class OutlineItem
    {
        public string Title { get; set; } = string.Empty;
        public int Level { get; set; }
        public int LineIndex { get; set; }
        public string DisplayText => new string(' ', (Level - 1) * 4) + (Level == 1 ? "📌 " : Level == 2 ? "🔸 " : "▪ ") + Title;
    }

    public partial class MainWindow : Window
    {
        private readonly MarkdownPipeline _pipeline;
        private readonly AiService _aiService = new AiService();
        private string _currentFilePath = string.Empty;
        private bool _isModified = false;
        private bool _isDarkMode = false;
        private bool _isReaderOnly = false;
        private bool _isOutlineVisible = true;
        private bool _isInitializing = false;
        private bool _isWebViewInitialized = false;
        private Timer? _debounceTimer;
        private CancellationTokenSource? _cts;
        private string _currentMaxWidth = "900px";

        public MainWindow()
        {
            InitializeComponent();

            _pipeline = new MarkdownPipelineBuilder()
                .UseAdvancedExtensions()
                .UseMathematics()
                .UseEmojiAndSmiley()
                .Build();

            CmbModels.ItemsSource = _aiService.Providers;
            CmbModels.SelectedIndex = 0;

            KeyDown += MainWindow_KeyDown;
            Closed += MainWindow_Closed;

            BrowserPreview.CoreWebView2InitializationCompleted += BrowserPreview_CoreWebView2InitializationCompleted;
            _ = BrowserPreview.EnsureCoreWebView2Async();

            TxtMarkdown.AddHandler(ScrollViewer.ScrollChangedEvent, new ScrollChangedEventHandler(TxtMarkdown_ScrollChanged));
        }

        private void MainWindow_Closed(object? sender, EventArgs e)
        {
            _debounceTimer?.Dispose();
            _cts?.Cancel();
            _cts?.Dispose();
        }

        private async void TxtMarkdown_ScrollChanged(object? sender, ScrollChangedEventArgs e)
        {
            if (_isReaderOnly || !_isWebViewInitialized || BrowserPreview?.CoreWebView2 == null) return;
            double verticalOffset = e.VerticalOffset;
            double maxOffset = e.ExtentHeight - e.ViewportHeight;
            double percentage = maxOffset > 0 ? verticalOffset / maxOffset : 0;
            string script = $"window.scrollTo(0, document.body.scrollHeight * {percentage.ToString("F2", System.Globalization.CultureInfo.InvariantCulture)});";
            await BrowserPreview.CoreWebView2.ExecuteScriptAsync(script);
        }

        private void BrowserPreview_CoreWebView2InitializationCompleted(object? sender, CoreWebView2InitializationCompletedEventArgs e)
        {
            if (e.IsSuccess)
            {
                _isWebViewInitialized = true;
                LoadWebViewSkeleton();
                NewDocument(promptSave: false);
            }
        }

        private void LoadWebViewSkeleton()
        {
            if (!_isWebViewInitialized || BrowserPreview?.CoreWebView2 == null) return;

            string cssTheme = _isDarkMode
                ? "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css"
                : "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.min.css";

            string bgColor = _isDarkMode ? "#1E1E1E" : "#FFFFFF";
            string textColor = _isDarkMode ? "#F0F0F0" : "#333333";        // 使用极亮白灰 #F0F0F0
            string headingColor = _isDarkMode ? "#FFFFFF" : "#111827";     // 纯白标题 #FFFFFF
            string tableBgEven = _isDarkMode ? "#2D2D2D" : "#F6F8FA";
            string tableBorder = _isDarkMode ? "#444444" : "#D0D7DE";
            string scrollThumb = _isDarkMode ? "#555555" : "#C1C1C1";
            string themeName = _isDarkMode ? "dark" : "default";

            string skeletonHtml = @"
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset='utf-8'/>
                <link rel='stylesheet' href='" + cssTheme + @"' id='theme-css'>
                <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css'>
                <script src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js'></script>
                <script src='https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js'></script>
                <script src='https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.0/mermaid.min.js'></script>
                <style>
                    ::-webkit-scrollbar { width: 8px; height: 8px; }
                    ::-webkit-scrollbar-track { background: transparent; }
                    ::-webkit-scrollbar-thumb { background: " + scrollThumb + @"; border-radius: 4px; }
                    body {
                        background-color: " + bgColor + @" !important;
                        color: " + textColor + @" !important;
                        max-width: " + _currentMaxWidth + @"; margin: 0 auto; padding: 24px 40px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Consolas', sans-serif;
                    }
                    
                    /* 强制覆盖 markdown-body 内部所有文本及标签颜色，防止被第三方 CSS 压制 */
                    .markdown-body, .markdown-body p, .markdown-body li, .markdown-body blockquote, .markdown-body span { 
                        background-color: transparent !important; 
                        color: " + textColor + @" !important; 
                    }
                    .markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4, .markdown-body h5, .markdown-body h6 { 
                        color: " + headingColor + @" !important; 
                    }
                    
                    .markdown-body table { border-collapse: collapse; width: 100%; margin: 16px 0; display: table !important; background-color: transparent !important; }
                    .markdown-body table th, .markdown-body table td { border: 1px solid " + tableBorder + @" !important; padding: 8px 14px; color: " + textColor + @" !important; }
                    .markdown-body table tr { background-color: " + (_isDarkMode ? "#1E1E1E" : "#FFFFFF") + @" !important; }
                    .markdown-body table tr:nth-child(2n) { background-color: " + tableBgEven + @" !important; }

                    .markdown-body pre { background-color: " + (_isDarkMode ? "#252526" : "#F6F8FA") + @" !important; border: 1px solid " + tableBorder + @"; border-radius: 6px; }
                    .markdown-body code { color: " + textColor + @" !important; }
                    .mermaid { background: transparent; text-align: center; margin: 20px 0; }
                    .katex { color: " + textColor + @" !important; }
                </style>
                <script>
                    function updateView(htmlContent) {
                        document.getElementById('content-body').innerHTML = htmlContent;
                        document.querySelectorAll('code.language-mermaid, pre code.language-mermaid').forEach(function(block) {
                            var pre = block.closest('pre') || block.parentElement;
                            var div = document.createElement('div');
                            div.className = 'mermaid';
                            div.textContent = block.textContent || block.innerText;
                            pre.parentNode.replaceChild(div, pre);
                        });
                        try {
                            mermaid.initialize({ startOnLoad: false, theme: '" + themeName + @"', securityLevel: 'loose' });
                            mermaid.run();
                        } catch(e) { console.error('Mermaid error:', e); }
                        if (typeof renderMathInElement !== 'undefined') {
                            renderMathInElement(document.body, {
                                delimiters: [
                                    {left: '$$', right: '$$', display: true},
                                    {left: '$', right: '$', display: false},
                                    {left: '\\(', right: '\\)', display: false},
                                    {left: '\\[', right: '\\]', display: true}
                                ],
                                throwOnError: false
                            });
                        }
                    }
                    function updateMaxWidth(widthVal) { document.body.style.maxWidth = widthVal; }
                    function updateTheme(cssHref, bgColor, textColor) {
                        document.getElementById('theme-css').href = cssHref;
                        document.body.style.backgroundColor = bgColor;
                        document.body.style.color = textColor;
                    }
                </script>
            </head>
            <body class='markdown-body' id='content-body'>
            </body>
            </html>";

            BrowserPreview.NavigateToString(skeletonHtml);
        }
        private void MainWindow_KeyDown(object? sender, KeyEventArgs e)
        {
            if (Keyboard.Modifiers == ModifierKeys.Control)
            {
                if (e.Key == Key.N) { BtnNew_Click(null, null); e.Handled = true; }
                else if (e.Key == Key.O) { BtnOpen_Click(null, null); e.Handled = true; }
                else if (e.Key == Key.S) { BtnSave_Click(null, null); e.Handled = true; }
            }
        }

        private void UpdateWindowTitle()
        {
            string fileName = string.IsNullOrEmpty(_currentFilePath) ? "Untitled-1" : Path.GetFileName(_currentFilePath);
            string mod = _isModified ? " •" : "";
            Title = $"{fileName}{mod} - SmartMarkDown";
        }

        private async void UpdatePreview()
        {
            if (!_isWebViewInitialized || BrowserPreview?.CoreWebView2 == null) return;
            string rawHtml = Markdown.ToHtml(TxtMarkdown.Text ?? string.Empty, _pipeline);
            string escapedHtml = HttpUtility.JavaScriptStringEncode(rawHtml);
            await BrowserPreview.CoreWebView2.ExecuteScriptAsync($"updateView('{escapedHtml}');");
        }

        private async void ApplyMaxWidthToView(string widthVal)
        {
            _currentMaxWidth = widthVal;
            if (_isWebViewInitialized && BrowserPreview?.CoreWebView2 != null)
            {
                await BrowserPreview.CoreWebView2.ExecuteScriptAsync($"updateMaxWidth('{widthVal}');");
            }
        }

        private void RefreshOutline(string text)
        {
            var outlineItems = new List<OutlineItem>();
            var lines = text.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);
            bool inCodeBlock = false;
            for (int i = 0; i < lines.Length; i++)
            {
                string line = lines[i].Trim();
                if (line.StartsWith("```")) { inCodeBlock = !inCodeBlock; continue; }
                if (!inCodeBlock && line.StartsWith("#"))
                {
                    int level = 0;
                    while (level < line.Length && line[level] == '#') level++;
                    if (level > 0 && level <= 3 && line.Length > level && char.IsWhiteSpace(line[level]))
                    {
                        outlineItems.Add(new OutlineItem { Title = line.Substring(level).Trim(), Level = level, LineIndex = i });
                    }
                }
            }
            ListOutline.ItemsSource = outlineItems;
        }

        private void TxtMarkdown_TextChanged(object? sender, TextChangedEventArgs e)
        {
            if (!_isInitializing) { _isModified = true; UpdateWindowTitle(); }
            string text = TxtMarkdown.Text ?? string.Empty;

            string cleanText = Regex.Replace(text, @"[*#`_>\[\]()!|-]", "");
            int wordCount = Regex.Matches(cleanText, @"[\w\u4e00-\u9fa5]+").Count;
            StatusWordCount.Text = $"{text.Length} 字符 | {wordCount} 词";

            RefreshOutline(text);

            _debounceTimer?.Dispose();
            _debounceTimer = new Timer(_ => Dispatcher.Invoke(UpdatePreview), null, 150, Timeout.Infinite);
        }

        private async void ListOutline_SelectionChanged(object? sender, SelectionChangedEventArgs e)
        {
            if (ListOutline.SelectedItem is OutlineItem item)
            {
                if (_isReaderOnly)
                {
                    if (_isWebViewInitialized && BrowserPreview?.CoreWebView2 != null)
                    {
                        string script = $@"
                        (function() {{
                            var headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                            for (var i = 0; i < headers.length; i++) {{
                                if (headers[i].textContent.trim() === {System.Text.Json.JsonSerializer.Serialize(item.Title)}) {{
                                    headers[i].scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                                    break;
                                }}
                            }}
                        }})();";
                        await BrowserPreview.CoreWebView2.ExecuteScriptAsync(script);
                    }
                }
                else
                {
                    if (item.LineIndex >= 0 && item.LineIndex < TxtMarkdown.LineCount)
                    {
                        int charIndex = TxtMarkdown.GetCharacterIndexFromLineIndex(item.LineIndex);
                        TxtMarkdown.Select(charIndex, 0);
                        TxtMarkdown.Focus();
                        TxtMarkdown.ScrollToHome();
                        for (int i = 0; i < item.LineIndex; i++) TxtMarkdown.LineDown();
                    }
                }
            }
        }

        private void MenuOpenRepo_Click(object? sender, RoutedEventArgs e)
        {
            try { Process.Start(new ProcessStartInfo("[https://github.com](https://github.com)") { UseShellExecute = true }); }
            catch (Exception ex) { MessageBox.Show($"无法打开链接: {ex.Message}"); }
        }

        private void BtnToggleOutline_Click(object? sender, RoutedEventArgs e)
        {
            _isOutlineVisible = !_isOutlineVisible;
            ColOutline.Width = _isOutlineVisible ? new GridLength(220) : new GridLength(0);
            ColOutlineSplitter.Width = _isOutlineVisible ? new GridLength(4) : new GridLength(0);
            MenuToggleOutline.IsChecked = _isOutlineVisible;
        }

        private void BtnToggleView_Click(object? sender, RoutedEventArgs e)
        {
            _isReaderOnly = !_isReaderOnly;
            ColEditor.Width = _isReaderOnly ? new GridLength(0) : new GridLength(1, GridUnitType.Star);
            ColSplitter.Width = _isReaderOnly ? new GridLength(0) : new GridLength(4);
            BtnToggleView.Content = _isReaderOnly ? "✏️ 双栏编辑" : "👁️ 纯阅读";
            MenuOnlyPreview.IsChecked = _isReaderOnly;
        }

        private void MenuWidthStandard_Click(object? sender, RoutedEventArgs e) { MenuWidthStandard.IsChecked = true; MenuWidthFull.IsChecked = false; MenuWidthNarrow.IsChecked = false; ApplyMaxWidthToView("900px"); }
        private void MenuWidthFull_Click(object? sender, RoutedEventArgs e) { MenuWidthStandard.IsChecked = false; MenuWidthFull.IsChecked = true; MenuWidthNarrow.IsChecked = false; ApplyMaxWidthToView("100%"); }
        private void MenuWidthNarrow_Click(object? sender, RoutedEventArgs e) { MenuWidthStandard.IsChecked = false; MenuWidthFull.IsChecked = false; MenuWidthNarrow.IsChecked = true; ApplyMaxWidthToView("700px"); }

        private void MenuWidthCustom_Click(object? sender, RoutedEventArgs e)
        {
            string input = Microsoft.VisualBasic.Interaction.InputBox("请输入版心宽度（例如：80% 或 1000px）：", "设置阅读版心宽度", _currentMaxWidth);
            if (!string.IsNullOrWhiteSpace(input))
            {
                if (Regex.IsMatch(input, @"^\d+(%|px)?$"))
                {
                    if (char.IsDigit(input[input.Length - 1])) input += "px";
                    ApplyMaxWidthToView(input);
                    MenuWidthStandard.IsChecked = false;
                    MenuWidthFull.IsChecked = false;
                    MenuWidthNarrow.IsChecked = false;
                }
                else
                {
                    MessageBox.Show("格式无效，请输入数字（如 800）或带单位的数值（如 80%, 1200px）。");
                }
            }
        }

        private bool PromptSaveIfModified()
        {
            if (!_isModified) return true;
            var res = MessageBox.Show("是否保存更改？", "提示", MessageBoxButton.YesNoCancel, MessageBoxImage.Question);
            if (res == MessageBoxResult.Yes) return PerformSave();
            return res == MessageBoxResult.No;
        }

        private bool PerformSave()
        {
            if (string.IsNullOrEmpty(_currentFilePath))
            {
                var dlg = new SaveFileDialog { Filter = "Markdown 文件 (*.md)|*.md", FileName = "Untitled.md" };
                if (dlg.ShowDialog() == true) _currentFilePath = dlg.FileName;
                else return false;
            }
            File.WriteAllText(_currentFilePath, TxtMarkdown.Text);
            _isModified = false;
            UpdateWindowTitle();
            return true;
        }

        private void NewDocument(bool promptSave = true)
        {
            if (promptSave && !PromptSaveIfModified()) return;
            _isInitializing = true;
            _currentFilePath = string.Empty;
            TxtMarkdown.Text = "# 欢迎使用 SmartMarkDown\n\n开始书写您的文档...";
            _isModified = false;
            _isInitializing = false;
            UpdateWindowTitle();
            UpdatePreview();
        }

        private void BtnNew_Click(object? sender, RoutedEventArgs e) => NewDocument(true);
        private void BtnOpen_Click(object? sender, RoutedEventArgs e)
        {
            if (!PromptSaveIfModified()) return;
            var dlg = new OpenFileDialog { Filter = "Markdown 文件 (*.md)|*.md" };
            if (dlg.ShowDialog() == true)
            {
                _isInitializing = true;
                _currentFilePath = dlg.FileName;
                TxtMarkdown.Text = File.ReadAllText(_currentFilePath);
                _isModified = false;
                _isInitializing = false;
                UpdateWindowTitle();
                UpdatePreview();
            }
        }
        private void BtnSave_Click(object? sender, RoutedEventArgs e) => PerformSave();
        private void BtnSaveAs_Click(object? sender, RoutedEventArgs e)
        {
            _currentFilePath = string.Empty;
            PerformSave();
        }
        private void BtnExportHtml_Click(object? sender, RoutedEventArgs e)
        {
            var dlg = new SaveFileDialog { Filter = "HTML 文件 (*.html)|*.html" };
            if (dlg.ShowDialog() == true)
            {
                string body = Markdown.ToHtml(TxtMarkdown.Text ?? string.Empty, _pipeline);
                File.WriteAllText(dlg.FileName, $"<!DOCTYPE html><html><body>{body}</body></html>");
            }
        }

        private async void BtnToggleTheme_Click(object? sender, RoutedEventArgs e)
        {
            _isDarkMode = !_isDarkMode;
            BtnThemeToggle.Content = _isDarkMode ? "☀️" : "🌙";
            MenuDarkMode.IsChecked = _isDarkMode;

            var resources = Application.Current.MainWindow.Resources;
            if (_isDarkMode)
            {
                resources["BgBrush"] = new SolidColorBrush(Color.FromRgb(0x1E, 0x1E, 0x1E));
                resources["CardBrush"] = new SolidColorBrush(Color.FromRgb(0x25, 0x25, 0x26));
                resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(0x3C, 0x3C, 0x3C));
                resources["TextPrimary"] = new SolidColorBrush(Color.FromRgb(0xD4, 0xD4, 0xD4));
                resources["TextMuted"] = new SolidColorBrush(Color.FromRgb(0x85, 0x85, 0x85));
                resources["ControlBg"] = new SolidColorBrush(Color.FromRgb(0x2D, 0x2D, 0x2D));
                resources["ControlHover"] = new SolidColorBrush(Color.FromRgb(0x38, 0x38, 0x38));
                resources["MenuPopupBg"] = new SolidColorBrush(Color.FromRgb(0x25, 0x25, 0x26));
                resources["MenuPopupBorder"] = new SolidColorBrush(Color.FromRgb(0x45, 0x45, 0x45));
                resources["MenuHighlight"] = new SolidColorBrush(Color.FromRgb(0x09, 0x47, 0x71));
            }
            else
            {
                resources["BgBrush"] = new SolidColorBrush(Color.FromRgb(0xFF, 0xFF, 0xFF));
                resources["CardBrush"] = new SolidColorBrush(Color.FromRgb(0xF3, 0xF3, 0xF3));
                resources["BorderBrush"] = new SolidColorBrush(Color.FromRgb(0xE5, 0xE5, 0xE5));
                resources["TextPrimary"] = new SolidColorBrush(Color.FromRgb(0x33, 0x33, 0x33));
                resources["TextMuted"] = new SolidColorBrush(Color.FromRgb(0x71, 0x71, 0x71));
                resources["ControlBg"] = new SolidColorBrush(Color.FromRgb(0xF8, 0xF8, 0xF8));
                resources["ControlHover"] = new SolidColorBrush(Color.FromRgb(0xE8, 0xE8, 0xE8));
                resources["MenuPopupBg"] = new SolidColorBrush(Color.FromRgb(0xFF, 0xFF, 0xFF));
                resources["MenuPopupBorder"] = new SolidColorBrush(Color.FromRgb(0xCC, 0xCC, 0xCC));
                resources["MenuHighlight"] = new SolidColorBrush(Color.FromRgb(0xE8, 0xE8, 0xE8));
            }

            if (_isWebViewInitialized && BrowserPreview?.CoreWebView2 != null)
            {
                string cssTheme = _isDarkMode
                    ? "[https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css](https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css)"
                    : "[https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.min.css](https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-light.min.css)";

                await BrowserPreview.CoreWebView2.ExecuteScriptAsync($"updateTheme('{cssTheme}', '{(_isDarkMode ? "#1E1E1E" : "#FFFFFF")}', '{(_isDarkMode ? "#D4D4D4" : "#333333")}');");
            }
        }

        private void CmbModels_SelectionChanged(object? sender, SelectionChangedEventArgs e)
        {
            if (CmbModels.SelectedItem is AiProvider selected) _aiService.CurrentProvider = selected;
        }

        private void BtnConfigKey_Click(object? sender, RoutedEventArgs e)
        {
            var provider = _aiService.CurrentProvider;
            if (provider == null) return;
            var dlg = new ApiKeyDialog(provider, _isDarkMode) { Owner = this };
            if (dlg.ShowDialog() == true)
            {
                provider.ApiKey = dlg.ApiKeyResult;
                if (!string.IsNullOrEmpty(dlg.SelectedModelId)) provider.ModelId = dlg.SelectedModelId;
            }
        }

        private async Task RunAiCommandAsync(string prompt, bool replaceSelection = false, bool append = false)
        {
            string selection = TxtMarkdown.SelectedText;
            string targetText = !string.IsNullOrWhiteSpace(selection) ? selection : TxtMarkdown.Text;
            if (string.IsNullOrWhiteSpace(targetText)) return;

            _cts?.Cancel();
            _cts = new CancellationTokenSource();

            try
            {
                PanelAiLoading.Visibility = Visibility.Visible;
                string result = await _aiService.ProcessAsync(prompt, targetText, _cts.Token);
                if (append) TxtMarkdown.AppendText("\n\n" + result);
                else if (replaceSelection && !string.IsNullOrWhiteSpace(selection)) TxtMarkdown.SelectedText = result;
                else TxtMarkdown.Text = result;
            }
            catch (OperationCanceledException) { /* 忽略取消异常 */ }
            catch (Exception ex) { MessageBox.Show(ex.Message, "AI 处理失败"); }
            finally { PanelAiLoading.Visibility = Visibility.Collapsed; }
        }

        private async void AiPolish_Click(object? sender, RoutedEventArgs e) => await RunAiCommandAsync("润色:", true);
        private async void AiSummarize_Click(object? sender, RoutedEventArgs e) => await RunAiCommandAsync("摘要:", false, true);
        private async void AiContinue_Click(object? sender, RoutedEventArgs e) => await RunAiCommandAsync("续写:", false, true);
        private async void AiTranslate_Click(object? sender, RoutedEventArgs e) => await RunAiCommandAsync("翻译:", true);

        private void ToolInsertBold_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"**{TxtMarkdown.SelectedText}**";
        private void ToolInsertItalic_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"*{TxtMarkdown.SelectedText}*";
        private void ToolInsertH2_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"\n## {TxtMarkdown.SelectedText}\n";
        private void ToolInsertCode_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"\n```csharp\n{TxtMarkdown.SelectedText}\n```\n";
        private void ToolInsertTable_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = "\n| 列1 | 列2 |\n|---|---|\n| 内容 | 内容 |\n";
        private void ToolInsertMermaid_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = "\n```mermaid\ngraph TD\nA-->B\n```\n";
        private void ToolInsertMath_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = "\n$$\nf(x) = x^2\n$$\n";
        private void ToolInsertLink_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.SelectedText = $"[链接](https://example.com)";
        private void ToolClear_Click(object? sender, RoutedEventArgs e) => TxtMarkdown.Clear();
        private void MenuExit_Click(object? sender, RoutedEventArgs e) => Application.Current.Shutdown();
    }
}