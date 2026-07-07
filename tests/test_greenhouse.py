import requests

url = "https://boards-api.greenhouse.io/v1/boards/nubank/jobs"

response = requests.get(url)

print(response.status_code)

data = response.json()

print(len(data["jobs"]))

print(data["jobs"][0]["title"])