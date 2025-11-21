import requests

url = "http://127.0.0.1:8000/chat"

while True:
    msg = input("You: ")
    data = {"message": msg}

    res = requests.post(url, json=data)

    if res.status_code != 200:
        print("Error:", res.text)
        continue

    reply = res.json()["reply"]
    print("Bot:", reply)
