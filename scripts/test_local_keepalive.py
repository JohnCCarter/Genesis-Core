import time

import requests


def test_connection():
    url = "http://localhost:3333/sse"
    print(f"Connecting to {url}...")
    try:
        with requests.get(url, stream=True, timeout=None) as response:
            print(f"Connected. Status: {response.status_code}")
            start_time = time.time()
            for line in response.iter_lines():
                if line:
                    print(f"[{time.time() - start_time:.1f}s] {line.decode('utf-8')}")
    except Exception as e:
        print(f"Connection dropped: {e}")


if __name__ == "__main__":
    test_connection()
