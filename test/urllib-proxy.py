
import urllib.request
from urllib.parse import urlparse, parse_qs

# Set your proxy URL and port here:
proxy_url = "http://127.0.0.1:1081"

def get_proxy_handler(proxy_url):
    return urllib.request.ProxyHandler({
        'http': proxy_url,
        'https': proxy_url,
    })

# Create a proxy handler:
handler = get_proxy_handler(proxy_url)

#  Open the URL using the proxy handler:
req = urllib.request.Request("https://translate.google.com/translate_a/single")
req.add_header('User-Agent', "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

proxy_support = urllib.request.ProxyHandler({
    'http': proxy_url,
    'https': proxy_url
})

opener = urllib.request.build_opener(proxy_support)
urllib.request.install_opener(opener)

response = opener.open(req)

print(response.read().decode('utf-8'))
