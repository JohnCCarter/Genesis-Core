import threading

import sseclient


def listen() -> None:
    messages = sseclient.SSEClient("http://localhost:3333/sse")
    for msg in messages:
        print(f"Event: {msg.event}")
        print(f"Data: {msg.data}")


def main() -> None:
    t = threading.Thread(target=listen, daemon=True)
    t.start()

    import time

    time.sleep(5)


if __name__ == "__main__":
    main()
