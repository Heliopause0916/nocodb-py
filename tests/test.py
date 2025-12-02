import os
import json
import time
from dotenv import load_dotenv
load_dotenv(dotenv_path="tests/.env", override=True)

api_key: str = os.getenv("NOCODB_API_KEY", "changeme")
base_url: str = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")

from nocodb_py import NocoDBClient

client = NocoDBClient(base_url=base_url, xc_token=api_key)

start_time = time.time()

print(client.list_projects(convert_time=True))

stop_time = time.time()
print(f"Time taken: {stop_time - start_time}")
