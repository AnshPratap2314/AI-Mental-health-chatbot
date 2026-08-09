import requests


URL = "http://127.0.0.1:8000/chat"


while True:

    message = input("You: ")

    if message.lower() in [
        "exit",
        "quit"
    ]:
        break

    response = requests.post(
        URL,
        json={
            "message": message
        }
    )

    if response.status_code != 200:

        print(
            "Error:",
            response.text
        )

        continue

    data = response.json()

    print(
        "Mode:",
        data["mode"]
    )

    print(
        "Risk Level:",
        data["risk_level"]
    )

    print(
        "Risk Score:",
        data["risk_score"]
    )

    print(
        "Bot:",
        data["reply"]
    )

    print()