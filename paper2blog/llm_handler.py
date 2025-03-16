import os
import logging
from typing import List, Dict
from openai import AsyncOpenAI
from paper2blog.model_types import ImageInfo

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    filename='llm_dialog.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


class LLMHandler:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE")
        )

    async def _generate_completion(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> str:
        # Log the input messages
        logging.info("Input messages to LLM:")
        for msg in messages:
            logging.info(f"Role: {msg['role']}")
            logging.info(f"Content: {msg['content']}\n")

        completion = await self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=temperature,
        )
        response = completion.choices[0].message.content

        # Log the LLM response
        logging.info("LLM Response:")
        logging.info(f"{response}\n")
        logging.info("-" * 80 + "\n")

        return response

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

# 学术博客生成指令

## 核心要求
1. **适当的口语化表达**：
- 任务描述：解析arXiv上关于LLM（大语言模型）和CS（计算机科学）的论文，生成一篇图文混排的学术博客。博客需贴近人类写作习惯，清晰传达论文核心内容，并在合适位置插入图片。
- 不要使用"你"、"我们"等人称代词建立对话感。博客内容的立场是作为一个第三方论文阅读者来描述，如果有偏主观的见解，请使用"笔者认为xxx"
- 需要关注核心的架构图，或者算法介绍图，并在文中使用一定篇幅进行讲解和引用，如"如图N所示，本算法首先。。。 然后。。。"
- 博客应包含标题、内容和总结， 其中内容部分可以根据需求分多个章节。# 是第一章节， ## 代表二级目录

2. 图文配合规则
- 每张图片需独占一行，格式为 ![图N: 描述。。。](图片路径不用修改)，其中N为图片编号。
- 图片描述需自然融入上下文，例如：
    "如图所示figure:fig1，该方法的架构分为三个主要模块..."
    "实验结果figure:fig3显示，该方法在准确率上显著优于基线模型..."
- 每张出现的图片都需要有对应的文字去描述，最起码有一段内容。

## 格式规范

1. 段落结构：
- 每章节3-5段，每段不超过150字
- 段落间用空行分隔
- 重点语句用**加粗**强调 
- 博客格式应为Markdown

2. 禁用内容：
- 专业术语缩写（首次出现需括号解释）

""",            
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
{text_content[:12000]}"""
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
            logging.error(f"Error in generate_blog_post: {str(e)}")
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
