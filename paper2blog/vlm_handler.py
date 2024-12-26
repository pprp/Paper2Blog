import aiohttp
import base64
from PIL import Image
import io

class VLMHandler:
    def __init__(self):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.api_key = "sk-mxnvgvluhpyxjpuvjjfevflefhxykpgxvtrqubmvmsytrgbp"  # Consider moving this to environment variables
        
    async def generate_caption(self, text_data: str, image_data: bytes) -> str:
        # Convert image bytes to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Chunk the text data into smaller segments (approximately 2000 characters per chunk)
        chunk_size = 2000
        text_chunks = [text_data[i:i+chunk_size] for i in range(0, len(text_data), chunk_size)]
        
        # Use the first chunk for context, as it's likely the most relevant
        context_text = text_chunks[0] + "..." if len(text_chunks) > 1 else text_data
        
        # Prepare the API payload with shortened context
        payload = {
            "model": "deepseek-ai/deepseek-vl2",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Please describe this image concisely in the context of this excerpt: {context_text}. Please use Chinese and English both to describe the image with a short sentence like 'This is a figure of ...; 这幅图描述了...' and there should be not '\n' in the sentence"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Make async API request
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
