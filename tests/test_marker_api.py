import requests
import json
import base64
import os
from pathlib import Path

post_data = {
    "filepath": "/Users/peyton/Workspace/Paper2Blog/tests/data/sample.pdf",
    # Add other params here
}

_json = requests.post("http://localhost:8024/marker", data=json.dumps(post_data)).json()
print(_json.keys())
# dict_keys(["format", "output", "images", "metadata", "success"])

print(_json["format"])  # markdown
print(_json["output"])  # markdown content
print(_json["metadata"])  # useless

save_dir = Path("/Users/peyton/Workspace/Paper2Blog/tmp/saved_pngs")
save_dir.mkdir(parents=True, exist_ok=True)

for img_name, img_data in _json["images"].items():
    img_path = save_dir / img_name
    # Decode base64 string to bytes
    img_bytes = base64.b64decode(img_data)
    with open(img_path, "wb") as f:
        f.write(img_bytes)

print(f"Images saved to {save_dir}")
