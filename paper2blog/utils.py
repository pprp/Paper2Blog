import os
import io
import base64
import requests
import numpy as np
from PIL import Image
from typing import Tuple, List
import json
from .models import ImageInfo
from .vlm_handler import VLMHandler
import re

def format_image_markdown(content: str) -> str:
    """
    Format markdown image references by combining the image and caption into a single line.
    
    Args:
        content (str): Input markdown content
        
    Returns:
        str: Formatted markdown content
    """
    # Pattern to match image reference and its following caption
    pattern = r'!\[\]\(([^)]+)\)\s*\n\s*<span[^>]*>.*?</span>(.+?)(?=\n\n|$)'
    
    def replace_match(match):
        img_path = match.group(1)
        caption = match.group(2).strip()
        return f'![{caption}]({img_path})'
    
    # Replace all matches in the content
    formatted_content = re.sub(pattern, replace_match, content, flags=re.DOTALL)
    return formatted_content


async def extract_content_from_pdf(
    pdf_path: str,
    extract_text: bool = True,
    extract_images: bool = True,
    max_images: int = 6,
) -> Tuple[str, List[ImageInfo]]:
    """
    Extract text and images from PDF using marker API

    Args:
        pdf_path: Path to the PDF file
        extract_text: Whether to extract text content
        extract_images: Whether to extract images
        max_images: Maximum number of images to extract (default 4, as first 4 are usually most relevant)

    Returns:
        Tuple containing:
        - Extracted text (markdown format)
        - List of ImageInfo objects
    """
    try:
        # Simple API call matching test_marker_api.py
        post_data = {"filepath": pdf_path}
        result = requests.post(
            "http://localhost:8024/marker", data=json.dumps(post_data)
        ).json()
        
        vlm_handler = VLMHandler()
        
        if not result.get("success"):
            print("Marker API failed to process PDF")
            return "", []

        # Extract markdown content if requested
        text_content = ""
        if extract_text:
            text_content = result.get("output", "")
            text_content = format_image_markdown(text_content)

        # Process images if requested
        images = []
        if extract_images and "images" in result:
            # Get first max_images from the images dict
            image_items = list(result["images"].items())[:max_images]

            for idx, (image_name, image_data) in enumerate(image_items):
                try:
                    # Decode base64 string to bytes first
                    image_bytes = base64.b64decode(image_data)
                    # Generate caption from image name using decoded bytes
                    caption = await vlm_handler.generate_caption(text_content, image_bytes)

                    # Save image temporarily
                    temp_path = os.path.join(
                        "/home/dongpeijie/workspace/Paper2Blog/tmp/saved_pngs", image_name
                    )
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)

                    # Write the already decoded bytes
                    with open(temp_path, "wb") as f:
                        f.write(image_bytes)

                    # Create ImageInfo object
                    image_info = ImageInfo(
                        caption=caption,
                        url=temp_path,
                        markdown=f"![{caption}]({temp_path})",
                    )
                    images.append(image_info)

                except Exception as e:
                    print(f"Error processing image {image_name}: {e}")
                    continue
        return text_content, images
    except Exception as e:
        print(f"Error extracting content from PDF: {e}")
        return "", []


def download_image(url: str) -> bytes:
    """Download image from URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def save_image(image_data: bytes, filename: str) -> str:
    """Save image data to file and return the path."""
    image = Image.open(io.BytesIO(image_data))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    image.save(filename)
    return filename
