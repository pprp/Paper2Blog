import io
import os
from bs4 import BeautifulSoup
import requests
from .llm_handler import LLMHandler
from .models import ConversionResponse, ImageInfo, BlogPost
from .utils import extract_content_from_pdf, format_table_to_markdown, download_image


class PaperConverter:
    def __init__(self):
        self.llm_handler = LLMHandler()

    async def convert_from_pdf(
        self, pdf_path: str, target_language: str = "en"
    ) -> ConversionResponse:
        """Convert PDF to blog post"""
        try:
            # Extract content from PDF using the file path directly
            text_content, images, tables = extract_content_from_pdf(pdf_path)

            # Format tables to markdown if any
            table_markdowns = [format_table_to_markdown(table) for table in tables]

            # Combine all content
            full_content = text_content
            if table_markdowns:
                full_content += "\n\n" + "\n\n".join(table_markdowns)

            try:
                # Generate blog post using LLM
                blog_post = await self.llm_handler.generate_blog_post(
                    full_content, target_language=target_language
                )

                if isinstance(blog_post, dict):
                    # Handle dictionary response
                    return ConversionResponse(
                        title=blog_post.get("title", ""),
                        content=blog_post.get("content", ""),
                        summary=blog_post.get("summary", ""),
                        language=target_language,
                        images=images,
                    )
                elif isinstance(blog_post, BlogPost):
                    # Handle BlogPost response
                    return ConversionResponse(
                        title=blog_post.title,
                        content=blog_post.content,
                        summary=blog_post.summary,
                        language=target_language,
                        images=images,
                    )
                else:
                    raise ValueError(
                        f"Unexpected response type from LLM handler: {type(blog_post)}"
                    )

            except Exception as e:
                return ConversionResponse(
                    language=target_language,
                    images=images,
                    error=f"Error in LLM processing: {str(e)}",
                )

        except Exception as e:
            return ConversionResponse(
                language=target_language, error=f"Error in PDF processing: {str(e)}"
            )

    async def convert_from_url(self, url: str, language: str) -> ConversionResponse:
        # Download and parse webpage
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text content
        text_content = soup.get_text()

        # Extract and process images
        image_infos = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                img_data = download_image(img_url)
                markdown = f"![{img.get('alt', '')}]({img_url})"
                image_infos.append(
                    ImageInfo(
                        caption=img.get("alt", ""), url=img_url, markdown=markdown
                    )
                )

        try:
            # Generate blog post using LLM
            blog_post = await self.llm_handler.generate_blog_post(
                text_content, target_language=language
            )

            if isinstance(blog_post, dict):
                return ConversionResponse(
                    title=blog_post.get("title", ""),
                    content=blog_post.get("content", ""),
                    summary=blog_post.get("summary", ""),
                    language=language,
                    images=image_infos,
                    tags=blog_post.get("tags", []),
                )
            elif isinstance(blog_post, BlogPost):
                return ConversionResponse(
                    title=blog_post.title,
                    content=blog_post.content,
                    summary=blog_post.summary,
                    language=language,
                    images=image_infos,
                )
            else:
                raise ValueError(
                    f"Unexpected response type from LLM handler: {type(blog_post)}"
                )

        except Exception as e:
            return ConversionResponse(
                language=language,
                images=image_infos,
                error=f"Error in LLM processing: {str(e)}",
            )
