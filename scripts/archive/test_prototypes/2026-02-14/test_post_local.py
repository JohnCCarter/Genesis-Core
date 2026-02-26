import requests


def main() -> None:
    session_id = "2e474f09028841868f1a8f61351bf005"
    url = f"http://localhost:3333/messages/?session_id={session_id}"
    payload = {"jsonrpc": "2.0", "method": "ping", "id": 1}

    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
