
import openai

OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
message = [
        {
            "role": "system",
            "content": "你是一个翻译助手，请把所有输入翻译成中文，不是拼音，不要出现emoji"
        },
        {
            "role": "user",
            "content": "hello world"
        }
    ]

client = openai.Client(base_url="http://localhost:4891/v1", api_key=OPENAI_API_KEY)  # <--- Change this line!
response = client.chat.completions.create(
    model='Meta-Llama-3-8B-Instruct.Q4_0.gguf',
    messages = message,
    max_tokens=100,  # adjust this to control the response length
    temperature=0.5,  # adjust this to control the response tone (e.g., more formal or casual),
)
print('response ', response)
print(response.choices[0].message.content)
