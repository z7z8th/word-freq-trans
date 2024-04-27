
import httpx

proxies = {"http": "http://127.0.0.1:1081", "https": "http://127.0.0.1:1081"}

with httpx.Client(proxies=proxies) as client:
    response = client.get("https://twitter.com/")
    print("IP address with proxy:", response.text)