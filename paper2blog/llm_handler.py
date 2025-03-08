import os
from typing import List, Dict
from openai import AsyncOpenAI
from .types import ImageInfo

from dotenv import load_dotenv

load_dotenv()


class LLMHandler:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
        )

    async def _generate_completion(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> str:
        completion = await self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=temperature,
        )
        return completion.choices[0].message.content

    async def translate_title(self, text_content: str, target_language: str) -> str:
        """Translate the title of the paper without modifying its content."""
        messages = [
            {
                "role": "system",
                "content": "You are a professional translator. Your task is to translate the title of an academic paper accurately without modifying its meaning.",
            },
            {
                "role": "user",
                "content": f"""Please translate only the title of this paper to {target_language}. Keep the translation accurate and faithful to the original meaning.

Paper content:
{text_content[:1000]}

Output format:
Just return the translated title without any additional text or formatting.""",
            },
        ]

        response = await self._generate_completion(messages)
        return response.strip()

    async def generate_blog(
        self, text_content: str, language: str, images: List[ImageInfo]
    ) -> Dict:
        """Generate a technical blog post from an academic paper."""
        try:
            # Determine language
            lang = "zh" if language.lower() in ["zh", "chinese", "中文"] else "en"

            # Define prompts based on language
            prompts = {
                "zh": {
                    "system": "你是一位专业的技术博主，擅长将学术论文转化为通俗易懂的技术博客。请用中文进行回复。请尽可能多详细的描述这篇文章内容。同时请根据图片的描述以及论文内容，将图片安排到合适的位置，并且添加对应段落来描述图片。",
                    "style": "保持技术准确性的同时确保可读性，突出创新点和实际应用价值。",
                },
                "en": {
                    "system": "You are a professional tech blogger who excels at transforming academic papers into accessible technical blog posts.",
                    "style": "Maintain technical accuracy while ensuring readability, highlighting innovations and practical value.",
                },
            }

            # Generate blog content
            messages = [
                {"role": "system", "content": prompts[lang]["system"]},
                {
                    "role": "user",
                    "content": f"""Write a technical blog post about this paper freely:
{prompts[lang]["style"]}

Available Images:
{self._format_images(images)}

Paper content:
{text_content[:2000]}""",
                },
            ]

            blog_content = await self._generate_completion(messages)

            # Get title and summary
            lines = blog_content.split("\n")
            title = next(
                (line.replace("# ", "") for line in lines if line.startswith("# ")),
                "Untitled",
            )

            # Translate title
            translated_title = await self.translate_title(text_content, language)

            # Extract summary
            summary_marker = "## Summary" if lang == "en" else "## 总结"
            summary = "No summary available" if lang == "en" else "暂无总结"

            summary_start = blog_content.find(summary_marker)
            if summary_start != -1:
                summary_end = blog_content.find("##", summary_start + 2)
                summary = (
                    blog_content[summary_start:summary_end].strip()
                    if summary_end != -1
                    else blog_content[summary_start:].strip()
                )

            return {
                "title": translated_title,
                "content": blog_content,
                "summary": summary,
                "tags": [],
            }

        except Exception as e:
            print(f"Error in generate_blog: {str(e)}")
            raise

    def _format_images(self, images: List[ImageInfo]) -> str:
        formatted_images = []
        for idx, img in enumerate(images, 1):
            # Convert absolute path to relative URL path
            relative_path = os.path.relpath(
                img.url, "/home/dongpeijie/workspace/Paper2Blog"
            )
            # Format markdown with web-accessible URL
            formatted_images.append(
                f"Figure {idx}: {img.caption}\n"
                f"Use exactly this markdown to insert the image: ![{img.caption}](http://localhost:8000/{relative_path})"
            )
        return "\n\n".join(formatted_images)

    async def generate_blog_post(
        self,
        text_content: str,
        target_language: str = "en",
        image_info: List[ImageInfo] = [],
    ):
        return await self.generate_blog(text_content, target_language, image_info)
