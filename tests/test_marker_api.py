import requests
import json
import base64
import os
from pathlib import Path

post_data = {
    "filepath": "/home/dongpeijie/workspace/LLMToolkit/difypaper/sent/2502_14377/2502_14377.pdf",
    # Add other params here
}

_json = requests.post("http://localhost:8024/marker", data=json.dumps(post_data)).json()
print(_json.keys())
# dict_keys(["format", "output", "images", "metadata", "success"])


print(_json["format"])  # markdown
print(_json["output"])  # markdown content
print(_json["metadata"])  # useless

# Create directories for both markdown and images
save_dir = Path("/home/dongpeijie/workspace/Paper2Blog/tmp/saved_pngs")
md_save_dir = Path("/home/dongpeijie/workspace/Paper2Blog/tmp/saved_md")
save_dir.mkdir(parents=True, exist_ok=True)
md_save_dir.mkdir(parents=True, exist_ok=True)

# Save markdown content
md_file_path = md_save_dir / "output.md"
with open(md_file_path, "w", encoding="utf-8") as f:
    f.write(_json["output"])
print(f"Markdown saved to {md_file_path}")

for img_name, img_data in _json["images"].items():
    img_path = save_dir / img_name
    # Decode base64 string to bytes
    img_bytes = base64.b64decode(img_data)
    with open(img_path, "wb") as f:
        f.write(img_bytes)



print(f"Images saved to {save_dir}")
