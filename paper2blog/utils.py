import os
import io
import base64
import requests
import numpy as np
from PIL import Image
from typing import Tuple, List
import pandas as pd
from .models import ImageInfo

def extract_content_from_pdf(
    pdf_content: bytes,
) -> Tuple[str, List[ImageInfo], List[pd.DataFrame]]:
    """
    Extract text, images, and tables from PDF using marker API
    
    Args:
        pdf_content: PDF file content in bytes
        
    Returns:
        Tuple containing:
        - Extracted text
        - List of ImageInfo objects
        - List of pandas DataFrames containing tables
    """
    try:
        # Send PDF to marker API
        files = {'file': ('document.pdf', pdf_content, 'application/pdf')}
        response = requests.post('http://localhost:8024/process', files=files)
        response.raise_for_status()
        result = response.json()
        
        # Extract text
        text_content = result.get('text', '')
        
        # Process images
        images = []
        for idx, img_data in enumerate(result.get('images', [])):
            try:
                # Decode base64 image
                image_bytes = base64.b64decode(img_data['data'])
                image = Image.open(io.BytesIO(image_bytes))
                
                # Skip small images (likely icons or decorations)
                if image.size[0] < 100 or image.size[1] < 100:
                    continue
                
                # Calculate image quality metrics
                img_array = np.array(image)
                if len(img_array.shape) >= 2:
                    std_dev = np.std(img_array)
                    if std_dev < 10:  # Skip near-empty images
                        continue
                
                # Generate unique filename
                filename = f"image_{idx + 1}.{img_data['format']}"
                
                # Save image temporarily
                temp_path = os.path.join("./tmp", filename)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(image_bytes)
                
                # Create ImageInfo object
                image_info = ImageInfo(
                    caption=f"Figure {len(images) + 1}",
                    url=temp_path,
                    markdown=f"![Figure {len(images) + 1}]({temp_path})",
                )
                images.append(image_info)
                
            except Exception as e:
                print(f"Error processing image: {e}")
                continue
        
        # Process tables
        tables = []
        for table_data in result.get('tables', []):
            try:
                data = table_data['data']
                if not data or not isinstance(data, list) or len(data) < 2:
                    continue
                    
                # Create DataFrame with proper headers
                headers = data[0]
                rows = data[1:]
                df = pd.DataFrame(rows, columns=headers)
                
                if df.size > 4:  # Skip very small tables
                    tables.append(df)
                    
            except Exception as e:
                print(f"Error processing table: {e}")
                continue
                
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
