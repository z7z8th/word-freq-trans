
import httpx
import json

OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
input_text = "Hello, how are you?"
msg = '{ "model": "Meta-Llama-3-8B-Instruct.Q4_0.gguf", "messages": [ { "role": "system", "content": "你是一个翻译助手，把所有输入翻译成中文，不是拼音" }, { "role": "user", "content": "the" } ] }'

client = httpx.Client(base_url="http://127.0.0.1:4891/v1", timeout=None)

response = client.post(
    "/chat/completions",
    headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json; charset=utf-8"},
    json = json.loads(msg),
)

print(response.json())


# import requests
# import json

# msg = '{ "model": "Meta-Llama-3-8B-Instruct.Q4_0.gguf", "messages": [ { "role": "system", "content": "你是一个翻译助手，把所有输入翻译成中文，不是拼音" }, { "role": "user", "content": "the" } ] }'
# url = "http://127.0.0.1:4891/v1/chat/completions"

# headers = {"Authorization": "Bearer ", "Content-Type": "application/json"}

# response = requests.post(url, headers=headers, json=json.loads(msg))
# print(response.choices[0].message.content)

