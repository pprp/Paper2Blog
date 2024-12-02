import io
import os
from typing import Union, List
import PyPDF2
import requests
from bs4 import BeautifulSoup
from .models import ConversionResponse, ImageInfo
from .llm_handler import LLMHandler
from .vlm_handler import VLMHandler
from .utils import extract_images_from_pdf, download_image


class PaperConverter:
    def __init__(self):
        self.llm = LLMHandler()
        self.vlm = VLMHandler()

    async def convert_from_pdf(
        self, pdf_content: bytes, language: str
    ) -> ConversionResponse:
        # Read PDF content
        pdf_file = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text()

        # Extract images
        images = extract_images_from_pdf(pdf_content)
        image_infos = []

        # Process images with VLM
        for img in images:
            caption = await self.vlm.generate_caption(img)
            # Save image and get URL (implementation needed)
            url = "./tmp"  # Placeholder
            markdown = f"![{caption}]({url})"
            image_infos.append(ImageInfo(caption=caption, url=url, markdown=markdown))

        # Generate blog content using LLM
        blog_content = await self.llm.generate_blog(text_content, language, image_infos)

        return ConversionResponse(
            title=blog_content["title"],
            content=blog_content["content"],
            language=language,
            images=image_infos,
            summary=blog_content["summary"],
            tags=blog_content["tags"],
        )

    async def convert_from_url(self, url: str, language: str) -> ConversionResponse:
        # Download and parse webpage
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text content (implementation depends on source website structure)
        text_content = soup.get_text()

        # Extract images
        image_infos = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                img_data = download_image(img_url)
                caption = await self.vlm.generate_caption(img_data)
                markdown = f"![{caption}]({img_url})"
                image_infos.append(
                    ImageInfo(caption=caption, url=img_url, markdown=markdown)
                )

        # Generate blog content using LLM
        blog_content = await self.llm.generate_blog(text_content, language, image_infos)

        return ConversionResponse(
            title=blog_content["title"],
            content=blog_content["content"],
            language=language,
            images=image_infos,
            summary=blog_content["summary"],
            tags=blog_content["tags"],
        )
