using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Threading.Tasks;

namespace SmartMarkDown
{
    public class AiProvider
    {
        public string Name { get; set; } = string.Empty;
        public string Endpoint { get; set; } = string.Empty;
        public string ModelId { get; set; } = string.Empty;
        public string ApiKey { get; set; } = string.Empty;
        public bool RequiresKey { get; set; } = true;
    }

    public class AiService
    {
        private static readonly HttpClient _http = new HttpClient { Timeout = TimeSpan.FromSeconds(60) };

        public List<AiProvider> Providers { get; } = new List<AiProvider>
        {
            new AiProvider
            {
                Name = "DeepSeek Chat",
                Endpoint = "https://api.deepseek.com/v1/chat/completions",
                ModelId = "deepseek-chat",
                ApiKey = ""
            },
            new AiProvider
            {
                Name = "DeepSeek Reasoner",
                Endpoint = "https://api.deepseek.com/v1/chat/completions",
                ModelId = "deepseek-reasoner",
                ApiKey = ""
            },
            new AiProvider
            {
                Name = "OpenAI GPT-4o Mini",
                Endpoint = "https://api.openai.com/v1/chat/completions",
                ModelId = "gpt-4o-mini",
                ApiKey = ""
            },
            new AiProvider
            {
                Name = "Kimi (Moonshot)",
                Endpoint = "https://api.moonshot.cn/v1/chat/completions",
                ModelId = "kimi-latest",
                ApiKey = ""
            },
            new AiProvider
            {
                Name = "智谱 (Zhipu)",
                Endpoint = "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                ModelId = "glm-4",
                ApiKey = ""
            },
            new AiProvider
            {
                Name = "小米 (Xiaomi MiMo)",
                Endpoint = "https://api.xiaomimimo.com/v1/chat/completions",
                ModelId = "mimo-v2.5-pro",
                ApiKey = ""
            },
            new AiProvider
            {
                Name = "Ollama (本地模型)",
                Endpoint = "http://localhost:11434/v1/chat/completions",
                ModelId = "qwen2.5:latest",
                ApiKey = "ollama",
                RequiresKey = false
            }
        };

        public AiProvider CurrentProvider { get; set; }

        public AiService()
        {
            CurrentProvider = Providers[0];
        }

        public async Task<string> ProcessAsync(string systemPrompt, string userContent)
        {
            if (CurrentProvider == null)
            {
                throw new InvalidOperationException("未选择任何 AI 模型。");
            }

            if (string.IsNullOrWhiteSpace(CurrentProvider.Endpoint))
            {
                throw new InvalidOperationException($"当前模型 [{CurrentProvider.Name}] 的请求端点 (Endpoint) 无效或为空！");
            }

            if (CurrentProvider.RequiresKey && string.IsNullOrWhiteSpace(CurrentProvider.ApiKey))
            {
                throw new InvalidOperationException($"请先点击顶部的 ⚙️ 按钮为 [{CurrentProvider.Name}] 配置有效的 API Key！");
            }

            var payload = new
            {
                model = CurrentProvider.ModelId,
                messages = new[]
                {
                    new { role = "system", content = systemPrompt },
                    new { role = "user", content = userContent }
                },
                temperature = 0.6
            };

            var request = new HttpRequestMessage(HttpMethod.Post, CurrentProvider.Endpoint.Trim());
            if (!string.IsNullOrWhiteSpace(CurrentProvider.ApiKey))
            {
                request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", CurrentProvider.ApiKey.Trim());
            }

            request.Content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");

            var response = await _http.SendAsync(request);
            var json = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception($"[{response.StatusCode}] {json}");
            }

            var node = JsonNode.Parse(json);
            return node?["choices"]?[0]?["message"]?["content"]?.ToString()?.Trim() ?? "AI 未返回有效内容";
        }
    }
}