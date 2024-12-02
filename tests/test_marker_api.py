import requests
import json

post_data = {
    "filepath": "/Users/peyton/Workspace/Paper2Blog/tests/data/sample.pdf",
    # Add other params here
}

_json = requests.post("http://localhost:8024/marker", data=json.dumps(post_data)).json()
print(_json.keys())
# dict_keys(["format", "output", "images", "metadata", "success"])
breakpoint()
print(_json["format"])  # markdown
print(_json["output"])  # markdown content
print(_json["metadata"])  # useless
print(
    type(_json["images"])
)  # dict: dict_keys(['_page_1_Figure_0.png', '_page_3_Figure_0.png', '_page_4_Figure_11.png', '_page_7_Figure_0.png', '_page_11_Figure_0.png', '_page_14_Picture_11.png'])
# in most cases, only the first 4 images are the ones we want
