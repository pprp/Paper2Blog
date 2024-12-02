import os
import io
import base64
import requests
import numpy as np
from PIL import Image
from typing import Tuple, List
import pandas as pd
import json
from .models import ImageInfo


def extract_content_from_pdf(
    pdf_path: str,
    extract_text: bool = True,
    extract_images: bool = True,
    max_images: int = 4,
) -> Tuple[str, List[ImageInfo], List[pd.DataFrame]]:
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
        - List of pandas DataFrames for tables (currently not supported by marker API)
    """
    try:
        # Prepare request to marker API
        post_data = {
            "filepath": pdf_path,
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            "http://localhost:8024/marker",
            data=json.dumps(post_data),
            headers=headers
        )
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        if not result.get("success"):
            print("Marker API failed to process PDF")
            return "", [], []

        # Extract markdown content if requested
        text_content = ""
        if extract_text:
            text_content = result.get("output", "")
            
        # Process images if requested
        images = []
        if extract_images and "images" in result:
            # Get first max_images from the images dict
            image_items = list(result["images"].items())[:max_images]
            
            for idx, (image_name, image_data) in enumerate(image_items):
                try:
                    # Generate caption from image name
                    # Remove prefix like '_page_1_' and file extension
                    caption = image_name.split('_', 3)[-1].rsplit('.', 1)[0]
                    
                    # Save image temporarily
                    temp_path = os.path.join("./tmp", image_name)
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    
                    # Image data is already in bytes, no need for base64 decode
                    with open(temp_path, "wb") as f:
                        f.write(image_data)

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

        # Tables are not currently supported by the marker API
        tables = []

        return text_content, images, tables

    except Exception as e:
        print(f"Error extracting content from PDF: {e}")
        return "", [], []


def format_table_to_markdown(df: pd.DataFrame) -> str:
    """Convert pandas DataFrame to markdown table format"""
    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]

    # Convert to markdown
    markdown = df.to_markdown(index=False)

    # Add caption
    markdown = f"Table:\n{markdown}\n"

    return markdown


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
