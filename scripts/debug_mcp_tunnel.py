import sys

import requests

# Default to the last known URL, but allow override
url = "https://codes-modelling-max-moderators.trycloudflare.com/sse"
if len(sys.argv) > 1:
    url = sys.argv[1]

print(f"Connecting to {url}...")

try:
    headers = {"Accept": "text/event-stream"}
    with requests.get(url, stream=True, headers=headers) as response:
        response.raise_for_status()
        print(f"Connected. Status: {response.status_code}")

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                print(decoded_line)
                if "data:" in decoded_line and "session_id" in decoded_line:
                    print("--- Endpoint received, stopping ---")
                    break
except Exception as e:
    print(f"Error: {e}")
