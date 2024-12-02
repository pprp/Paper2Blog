import io
from typing import List
import PyPDF2
import requests
from PIL import Image

def extract_images_from_pdf(pdf_content: bytes) -> List[bytes]:
    """Extract images from PDF content."""
    images = []
    pdf = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    
    for page in pdf.pages:
        for image_file_object in page.images:
            images.append(image_file_object.data)
    
    return images

def download_image(url: str) -> bytes:
    """Download image from URL."""
    response = requests.get(url)
    return response.content

def save_image(image_data: bytes, filename: str) -> str:
    """Save image data to file and return the path."""
    image = Image.open(io.BytesIO(image_data))
    image.save(filename)
    return filename
