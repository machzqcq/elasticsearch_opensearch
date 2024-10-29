import requests
import random
import time
import urllib3

url = 'http://data-prepper:2020/log/ingest'
source_ips = [f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(10)]

while True:
    log_entry = {
        "count_source_ip": random.randint(1, 1000),
        "source_ip": random.choice(source_ips)
    }
    try:
        response = requests.post(url, json=[log_entry], timeout=30)
    except Exception as e:
        print("Request timed out")
        continue
    print(f"Sent: [{log_entry}], Response: {response.status_code}")
    time.sleep(2)  # Adjust the sleep time as needed