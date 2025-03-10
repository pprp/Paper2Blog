import os
import logging
from typing import List, Dict, Optional
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from .types import ImageInfo, BlogPost
from .utils import extract_content_from_pdf
from .llm_handler import LLMHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="agent_log.log",
)
logger = logging.getLogger(__name__)


class BlogGenerationAgent:
    """使用LangChain Agent框架生成博客内容的代理类"""

    def __init__(self, api_key: Optional[str] = None, temperature: float = 0.7):
        """初始化博客生成代理

        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量获取
            temperature: 生成文本的随机性，0-1之间，越高越随机
        """
        # 初始化LLM
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供OpenAI API密钥")

        self.llm = OpenAI(
            temperature=temperature, max_tokens=1000, api_key=self.api_key
        )
        self.llm_handler = LLMHandler()

        # 定义生成博客段落的Prompt模板
        self.blog_section_prompt = PromptTemplate(
            input_variables=["text", "context", "style_guide"],
            template="""你是一位专业的技术博主，擅长将学术论文转化为通俗易懂的技术博客。请用中文进行回复。

请将以下论文片段转换为博客段落，遵循以下要求：

1. **内容**：将论文片段转化为详细的博客段落，至少300字。用简单的语言和生动的例子解释核心概念。
2. **风格**：使用{style_guide}的语调，保持自然、人性化的表达。避免过于学术化的术语，除非有解释。
3. **图片**：如果文本提到图片（如"图1"），在适当位置插入[Figure X]作为占位符。
4. **上下文**：使用以下上下文确保逻辑流畅，避免重复：{context}

论文片段：
{text}

博客段落：""",
        )

        # 创建LLMChain用于生成博客段落
        self.blog_section_chain = LLMChain(
            llm=self.llm, prompt=self.blog_section_prompt
        )

        # 定义Tool，封装生成博客段落的功能
        self.generate_section_tool = Tool(
            name="生成博客段落",
            func=lambda inputs: self.blog_section_chain.run(
                {
                    "text": inputs["text"],
                    "context": inputs["context"],
                    "style_guide": inputs.get("style_guide", "友好且对话式"),
                }
            ),
            description="根据论文片段生成详细的博客段落，确保清晰度和吸引力。",
        )

        # 初始化Agent
        self.agent = initialize_agent(
            tools=[self.generate_section_tool],
            llm=self.llm,
            agent_type="zero-shot-react-description",
            verbose=True,
        )

    async def generate_blog_with_agent(
        self, text_chunks: List[str], image_info: List[ImageInfo]
    ) -> str:
        """使用Agent分段生成博客内容。

        Args:
            text_chunks: 分块的论文文本。
            image_info: 包含图片信息的列表。

        Returns:
            完整的博客内容。
        """
        blog_sections = []
        previous_context = (
            "这篇博客介绍了一篇关于大型语言模型(LLMs)的论文。"  # 初始上下文
        )

        for i, chunk in enumerate(text_chunks):
            logger.info(f"正在生成第{i+1}段...")
            # 构建Agent输入
            agent_input = {
                "text": chunk,
                "context": previous_context,
                "style_guide": "友好且对话式",  # 可动态调整
            }

            # 调用Agent生成当前段落
            try:
                section = self.agent.run(f"根据以下输入生成博客段落: {agent_input}")
                blog_sections.append(section)

                # 更新上下文：提取当前段落的核心信息，避免过长
                previous_context = (
                    f"上一段讨论了: {section[:100]}..."
                    if len(section) > 100
                    else section
                )
            except Exception as e:
                logger.error(f"生成段落{i+1}时出错: {str(e)}")
                blog_sections.append(f"[生成此段落时出错: {str(e)}]")

        return "\n\n".join(blog_sections)  # 用换行分隔段落，便于阅读

    async def generate_blog(
        self, pdf_path: str, target_language: str = "zh"
    ) -> BlogPost:
        """生成完整的图文混排博客。

        Args:
            pdf_path: PDF文件路径。
            target_language: 目标语言，默认为中文。

        Returns:
            包含博客标题和内容的BlogPost对象。
        """
        try:
            # 从PDF提取内容
            logger.info(f"从PDF提取内容: {pdf_path}")
            text_content, images = await extract_content_from_pdf(pdf_path)

            # 将提取的文本分块
            text_chunks = self._split_text(text_content)

            # 使用Agent生成博客内容
            logger.info("使用Agent生成博客内容")
            full_blog_text = await self.generate_blog_with_agent(text_chunks, images)

            # 处理图片引用
            for img in images:
                # 替换图片引用
                placeholder = f"[Figure {img.caption.split(':')[0] if ':' in img.caption else img.caption}]"
                full_blog_text = full_blog_text.replace(placeholder, img.markdown)

            # 生成标题
            logger.info("生成博客标题")
            title = await self.llm_handler.translate_title(
                text_content, target_language
            )

            return BlogPost(title=title, content=full_blog_text)

        except Exception as e:
            logger.error(f"生成博客时出错: {str(e)}")
            raise

    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """将文本分割成适合处理的块。

        Args:
            text: 要分割的文本。
            chunk_size: 每块的大致字符数。

        Returns:
            分割后的文本块列表。
        """
        # 按段落分割
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# 示例调用
if __name__ == "__main__":
    import asyncio

    async def main():
        agent = BlogGenerationAgent()
        pdf_path = "path/to/your/pdf.pdf"
        blog_post = await agent.generate_blog(pdf_path)
        print("\n生成的博客内容:\n")
        print(f"# {blog_post.title}\n\n{blog_post.content}")

    asyncio.run(main())
