# SmartMarkDown - 现代 AI 驱动的 Markdown 创作空间



# Modern AI-Powered Markdown Creation Space



SmartMarkDown 是一款基于 WPF、WebView2 和 .NET 8 构建的现代化 Markdown 编辑与阅读器。

SmartMarkDown is a modern Markdown editor and reader built on WPF, WebView2, and .NET 8.

它融合了 VS Code 的极简设计美学与强大的 AI 赋能，专为追求效率与沉浸式书写的创作者打造。

Combining the minimalist design aesthetics of VS Code with powerful AI empowerment, it is tailored for creators who pursue efficiency and immersive writing.

---

<img width="1483" height="992" alt="image" src="https://github.com/user-attachments/assets/01e6739a-1f7c-4f8b-b30e-baa332830859" />

## 🌟 主要功能



## 🌟 Key Features



### 🖋️ 核心创作体验



### 🖋️ Core Creation Experience



* **双栏实时预览**：内置 Chromium 内核渲染，编辑与预览同步。


* **Dual-Column Real-Time Preview**: Built-in Chromium engine rendering for synchronized editing and preview.


* **极简模式**：支持切换至“纯阅读”视图，消除界面干扰，专注于内容本身。


* **Minimalist Mode**: Supports switching to a "Pure Reading" view to eliminate interface distractions and focus entirely on content.


* **多主题支持**：内置 **VS Code 经典 Dark+ 主题**与浅色模式，动态切换色彩，沉浸感极强。


* **Multi-Theme Support**: Features the **classic VS Code Dark+ theme** and light mode, enabling dynamic color switching with high immersion.


* **文件管理**：支持 Markdown 文件编辑、保存、另存为及一键导出为独立 HTML 文件。


* **File Management**: Supports editing, saving, "Save As" for Markdown files, and one-click export to standalone HTML files.



### 🤖 AI 智能赋能 (集成 OpenAI/DeepSeek 协议)



### 🤖 AI Empowerment (Integrated OpenAI/DeepSeek Protocols)



* **智能润色**：一键修复语法错误并提升文风。


* **Smart Polishing**: One-click correction of grammar errors and style enhancement.


* **自动摘要**：为长文生成核心要点（支持 Markdown 引用格式）。


* **Auto-Summary**: Generates core key points for long articles (supporting Markdown citation format).


* **上下文续写**：根据现有内容，逻辑连贯地进行续写。


* **Contextual Continuation**: Continues writing logically and coherently based on existing content.


* **多模型切换**：支持 OpenAI、DeepSeek、本地 Ollama 模型，可灵活配置 API Key。


* **Multi-Model Switching**: Supports OpenAI, DeepSeek, and local Ollama models with flexible API Key configuration.



### 📊 专业排版支持



### 📊 Professional Typography Support



* **Mermaid 流程图**：支持直接在代码块中编写并实时渲染流程图、时序图、甘特图。


* **Mermaid Flowcharts**: Write and render flowcharts, sequence diagrams, and Gantt charts in code blocks in real time.


* **LaTeX 数学公式**：内置 KaTeX 引擎，支持 $E=mc^2$ 等行内与块级公式渲染。


* **LaTeX Mathematical Formulas**: Built-in KaTeX engine supporting inline and block formula rendering such as $E=mc^2$.


* **美化表格**：GFM 表格支持，自动应用斑马纹与高亮边框。


* **Enhanced Tables**: GFM table support with automatic zebra striping and highlighted borders.



---

## 🛠️ 技术栈



## 🛠️ Tech Stack



* **UI 框架**: WPF (.NET 8.0)


* **UI Framework**: WPF (.NET 8.0)


* **渲染引擎**: Microsoft.Web.WebView2


* **Rendering Engine**: Microsoft.Web.WebView2


* **Markdown 解析**: Markdig


* **Markdown Parser**: Markdig


* **数学公式**: KaTeX


* **Math Formulas**: KaTeX


* **图表渲染**: Mermaid.js


* **Chart Rendering**: Mermaid.js



---

## 🚀 快速开始



## 🚀 Quick Start



1. **克隆项目**：确保安装了 .NET 8.0 SDK。


2. **Clone Project**: Ensure .NET 8.0 SDK is installed.


3. **构建项目**：使用 Visual Studio 2022/2026 打开 `SmartMarkDown.csproj`，重新生成解决方案。


4. **Build Project**: Open `SmartMarkDown.csproj` using Visual Studio 2022/2026 and rebuild the solution.


5. **配置模型**：首次运行时，点击顶部模型设置按钮，填入您的 API Key 即可使用 AI 功能。


6. **Configure Model**: Upon first run, click the model settings button at the top and enter your API Key to enable AI features.


7. **运行**：按 F5 启动应用。


8. **Run**: Press F5 to launch the application.



---

## 💡 使用说明



## 💡 Usage Instructions



* **快捷键**：`Ctrl + N` 新建文件，`Ctrl + O` 打开文件，`Ctrl + S` 保存文件。


* **Shortcuts**: `Ctrl + N` for new file, `Ctrl + O` for open file, `Ctrl + S` for save file.


* **AI 建议**：选中文字后点击顶部 AI 按钮，仅处理选区内容；不选中则处理全文。


* **AI Suggestions**: Select text and click the top AI button to process only the selected content; if nothing is selected, it processes the entire text.



---

## 📝 许可证



## 📝 License



MIT License

MIT License
