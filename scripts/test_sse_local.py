import threading

import sseclient


def listen():
    messages = sseclient.SSEClient("http://localhost:3333/sse")
    for msg in messages:
        print(f"Event: {msg.event}")
        print(f"Data: {msg.data}")


if __name__ == "__main__":
    # Start listening in a thread (since it blocks)
    t = threading.Thread(target=listen, daemon=True)
    t.start()

    # Keep alive for a few seconds to receive initial events
    import time

    time.sleep(5)
