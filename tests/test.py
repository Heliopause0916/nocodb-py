import os
import json
from dotenv import load_dotenv
load_dotenv(dotenv_path="tests/.env", override=True)

api_key: str = os.getenv("NOCODB_API_KEY", "changeme")
base_url: str = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")

from nocodb_py import NocoDBClient

client = NocoDBClient(base_url=base_url, xc_token=api_key)

print(client.server_version())
print(client.user_id())
print(client.user_email())
print(client.user_display_name())
