from openai import OpenAI

# 配置你的 DeepSeek Key
# 为了安全，我这里用星号代替了部分，请确保你代码里填的是完整的
MY_API_KEY = "sk-368e11c3ac0048f485f16ad3bfff06de"

client = OpenAI(
    api_key=MY_API_KEY,
    base_url="https://api.deepseek.com"
)

print("正在呼叫 DeepSeek-V3...")

try:
    response = client.chat.completions.create(
        model="deepseek-chat",  # DeepSeek-V3 的模型代码
        messages=[
            {"role": "user", "content": "你是哪个版本的模型？是DeepSeek-V2还是V3？请根据你的知识库回答。"}
        ],
        stream=False
    )

    print("✅ 连接成功！模型返回如下：")
    print("-" * 30)
    print(response.choices[0].message.content)
    print("-" * 30)

except Exception as e:
    print("❌ 连接失败。原因如下：")
    print(e)