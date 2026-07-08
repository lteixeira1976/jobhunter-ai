import re
import requests

base_url = "https://portal.gupy.io"
js_path = "/_next/static/chunks/pages/job-search/%5Bpid%5D-ceca1fff29fea791.js"

url = base_url + js_path

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=10)

text = response.text

print(response.status_code)
print("Tamanho JS:", len(text))

patterns = [
    r'https://[^"\']+',
    r'/api/[^"\']+',
    r'api\.[^"\']+',
    r'jobs[^"\']+',
    r'job-search[^"\']+'
]

for pattern in patterns:

    matches = re.findall(pattern, text)

    print()
    print(f"Pattern: {pattern}")
    print(f"Total: {len(matches)}")

    for item in matches[:50]:
        print(item[:300])