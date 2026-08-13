using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace SmartMarkDown
{
    public partial class ApiKeyDialog : Window
    {
        public string ApiKeyResult { get; private set; } = string.Empty;
        public string SelectedModelId { get; private set; } = string.Empty;

        // 为常见厂商提供子系列/版本候选列表
        private static readonly Dictionary<string, List<string>> _modelSubSeries = new Dictionary<string, List<string>>
        {
            { "DeepSeek Chat", new List<string> { "deepseek-chat" } },
            { "DeepSeek Reasoner", new List<string> { "deepseek-reasoner" } },
            { "OpenAI GPT-4o Mini", new List<string> { "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo" } },
            { "Kimi (Moonshot)", new List<string> { "kimi-latest", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k" } },
            { "智谱 (Zhipu)", new List<string> { "glm-4", "glm-4-flash", "glm-4v", "glm-3-turbo" } },
            { "小米 (Xiaomi MiMo)", new List<string> { "mimo-v2.5-pro", "mimo-standard" } },
            { "Ollama (本地模型)", new List<string> { "qwen2.5:latest", "llama3:latest", "deepseek-r1:latest", "mistral:latest" } }
        };

        public ApiKeyDialog(AiProvider provider, bool isDarkMode)
        {
            InitializeComponent();

            // 龙虾主题的配色逻辑
            if (isDarkMode)
            {
                Background = new SolidColorBrush(Color.FromRgb(0x2D, 0x2D, 0x2D));
                TxtProviderName.Foreground = Brushes.White;
            }

            TxtProviderName.Text = $"🦞 {provider.Name} 模式";
            TxtBoxKey.Password = provider.ApiKey;

            // 绑定子系列下拉菜单
            if (_modelSubSeries.TryGetValue(provider.Name, out var subList))
            {
                CmbSubModels.ItemsSource = subList;
                if (subList.Contains(provider.ModelId))
                {
                    CmbSubModels.SelectedItem = provider.ModelId;
                }
                else
                {
                    CmbSubModels.SelectedIndex = 0;
                }
            }
            else
            {
                CmbSubModels.ItemsSource = new List<string> { provider.ModelId };
                CmbSubModels.SelectedIndex = 0;
            }
        }

        private void BtnConfirm_Click(object sender, RoutedEventArgs e)
        {
            ApiKeyResult = TxtBoxKey.Password.Trim();
            SelectedModelId = CmbSubModels.SelectedItem?.ToString() ?? string.Empty;
            DialogResult = true;
            Close();
        }

        private void BtnCancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}