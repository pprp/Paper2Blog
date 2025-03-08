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

    async def generate_blog_post(
        self,
        text_content: str,
        target_language: str = "en",
        image_info: List[ImageInfo] = [],
    ):
        """Generate a technical blog post from an academic paper in one shot."""
        try:
            # Determine language
            lang = "zh" if target_language.lower() in ["zh", "chinese", "中文"] else "en"
            
            # Format images for inclusion in the prompt
            formatted_images = self._format_images(image_info)
            
            # Define system prompts based on language
            system_prompts = {
                "zh": """你是一位专业的技术博主，擅长将学术论文转化为通俗易懂的技术博客。请用中文进行回复。

请按照以下要求生成博客：
1. 生成博客内容应该尽可能详细，覆盖核心创新点
2. 保留图片描述，原文中的，并保留markdown格式图片语法 如： ![](image_xx.png)，并将图片放在合适的位置
3. 博客应包含标题、内容和总结
4. 博客格式应为Markdown
5. 博客标题应以"# "开头
6. 总结部分应以"## 总结"开头
7. 保持技术准确性的同时确保可读性，突出创新点和实际应用价值""",
                
                "en": """You are a professional tech blogger who excels at transforming academic papers into accessible technical blog posts.

Please generate a blog post following these requirements:
1. The blog content should be as detailed as possible, covering the core innovations
2. Preserve image descriptions from the original paper and maintain markdown image syntax like: ![](image_xx.png), placing images in appropriate locations
3. The blog should include a title, content, and summary
4. The blog format should be Markdown
5. The blog title should start with "# "
6. The summary section should start with "## Summary"
7. Maintain technical accuracy while ensuring readability, highlighting innovations and practical value"""
            }
            
            # Generate blog content in one shot
            messages = [
                {"role": "system", "content": system_prompts[lang]},
                {
                    "role": "user",
                    "content": f"""Here is the academic paper to transform into a blog post:

Available Images:
{formatted_images}

Paper content:
{text_content}"""
                },
            ]

            blog_content = await self._generate_completion(messages)
            
            # Extract title from the generated content
            lines = blog_content.split("\n")
            title = next(
                (line.replace("# ", "") for line in lines if line.startswith("# ")),
                "Untitled",
            )
            
            return {
                "title": title,
                "content": blog_content,
                "summary": "",  # No separate summary extraction needed as it's part of the blog content
                "tags": []
            }

        except Exception as e:
            print(f"Error in generate_blog_post: {str(e)}")
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
