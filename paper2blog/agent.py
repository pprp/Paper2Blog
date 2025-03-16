import os
import logging
from typing import List, Dict, Optional
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI 
from paper2blog.model_types import ImageInfo, BlogPost
from paper2blog.utils import extract_content_from_pdf
from paper2blog.llm_handler import LLMHandler
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="agent_log.log",
)
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BlogGenerationAgent:
    def __init__(self, api_key: Optional[str] = None, temperature: float = 0.7):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供OpenAI API密钥")

        self.llm = OpenAI(
            temperature=temperature, max_tokens=1000, api_key=self.api_key, base_url=os.getenv("OPENAI_API_BASE")
        )
        self.llm_handler = LLMHandler()

        self.blog_section_prompt = PromptTemplate(
            input_variables=["text", "context", "style_guide"],
            template="""你是一位专业的技术博主，擅长将学术论文转化为通俗易懂的技术博客。请用中文进行回复。

请将以下论文片段转换为博客段落，遵循以下要求：

1. **内容**：将论文片段转化为详细的博客段落，至少3000字。
2. **风格**：使用{style_guide}的语调，保持自然、人性化的表达。避免过于学术化的术语，除非有解释。
3. **图片**：如果文本提到图片（如"图1"），在适当位置插入[Figure X]作为占位符。
4. **上下文**：使用以下上下文确保逻辑流畅，避免重复：{context}

论文片段：
{text}

博客段落：""",
        )

        self.blog_section_chain = LLMChain(
            llm=self.llm, prompt=self.blog_section_prompt
        )

        self.generate_section_tool = Tool(
            name="生成博客段落",
            func=lambda inputs: self.blog_section_chain.run(
                text=inputs.get("text", inputs) if isinstance(inputs, dict) else inputs,
                context=inputs.get("context", "") if isinstance(inputs, dict) else "",
                style_guide=inputs.get("style_guide", "友好且对话式") if isinstance(inputs, dict) else "友好且对话式"
            ),
            description="""根据论文片段生成详细的博客段落。
            输入格式可以是字符串（论文片段）或字典（包含 text, context, style_guide）。
            将生成一个详细的、通俗易懂的博客段落。""",
        )

        self.agent = initialize_agent(
            tools=[self.generate_section_tool],
            llm=self.llm,
            agent_type="zero-shot-react-description",
            verbose=True,
        )

    async def generate_blog_with_agent(
        self, text_chunks: List[str], image_info: List[ImageInfo]
    ) -> str:
        blog_sections = []
        previous_context = "这篇博客介绍了一篇关于大型语言模型(LLMs)的论文。"

        for i, chunk in enumerate(text_chunks):
            logger.info(f"正在生成第{i+1}段...")
            try:
                # 直接传递文本内容作为输入
                section = self.agent.run(chunk)
                logger.info(f"第{i+1}段生成完成")
                if section:
                    blog_sections.append(section)
                    previous_context = (
                        f"上一段讨论了: {section[:100]}..."
                        if len(section) > 100
                        else section
                    )
                else:
                    logger.error(f"第{i+1}段生成失败：返回内容为空")
            except Exception as e:
                logger.error(f"生成第{i+1}段时发生错误: {str(e)}")
                continue

        if not blog_sections:
            raise ValueError("没有成功生成任何博客内容")

        return "\n\n".join(blog_sections)

    async def generate_blog(
        self, pdf_path: str, target_language: str = "zh"
    ) -> BlogPost:
        logger.info(f"从PDF提取内容: {pdf_path}")
        text_content, images = await extract_content_from_pdf(pdf_path)

        text_chunks = self._split_text(text_content)

        logger.info("使用Agent生成博客内容")
        full_blog_text = await self.generate_blog_with_agent(list(text_chunks.values()), images)

        for img in images:
            placeholder = f"[Figure {img.caption.split(':')[0] if ':' in img.caption else img.caption}]"
            full_blog_text = full_blog_text.replace(placeholder, img.markdown)

        logger.info("生成博客标题")
        title = await self.llm_handler.translate_title(
            text_content, target_language
        )

        return BlogPost(title=title, content=full_blog_text)

    def _split_text(self, text: str) -> Dict[str, str]:
        sections = {}
        lines = text.split("\n")
        current_section = None
        current_content = []

        # 定义章节映射
        section_mappings = {
            'abstract': 'Abstract',
            'summary': 'Abstract',
            'introduction': 'Introduction',
            'motivation': 'Introduction',
            'related work': 'Related Work',
            'background': 'Related Work',
            'methodology': 'Method',
            'method': 'Method',
            'approach': 'Method',
            'framework': 'Method',
            'evaluation': 'Experiments',
            'experiment': 'Experiments',
            'experiments': 'Experiments',
            'result': 'Experiments',
            'results': 'Experiments',
            'implementation': 'Experiments',
            'discussion': 'Conclusion',
            'conclusion': 'Conclusion'
        }

        # 结束章节
        stop_sections = {'references', 'appendix', 'acknowledgements', 'acknowledgments', 'bibliography'}

        def is_section_header(line: str) -> bool:
            # 如果行太长，可能不是标题
            if len(line) > 100:
                return False
            # 如果包含太多标点符号，可能不是标题
            if len(re.findall(r'[,.;:]', line)) > 2:
                return False
            # 如果有多个换行，可能不是标题
            if line.count('\n') > 1:
                return False
            return True

        def normalize_line(line: str) -> str:
            # 移除数字编号
            clean = re.sub(r'^\d+[\.\)]\s*', '', line)
            # 移除特殊字符
            clean = re.sub(r'^[#\s]+', '', clean)
            # 转换为小写并去除首尾空格
            return clean.lower().strip()

        def find_matching_section(normalized: str) -> str:
            # 先尝试完全匹配
            for key, section in section_mappings.items():
                if normalized == key:
                    logger.info(f"Exact match: '{normalized}' -> {section}")
                    return section

            # 然后尝试关键词匹配
            for key, section in section_mappings.items():
                # 对于特殊关键词，使用更宽松的匹配
                if key in ['methodology', 'evaluation', 'method', 'experiment']:
                    if key in normalized:
                        logger.info(f"Special keyword match: '{key}' in '{normalized}' -> {section}")
                        return section
                # 对于其他关键词
                else:
                    # 如果是短词，使用单词边界匹配
                    if len(key) <= 4:
                        if re.search(r'\b' + re.escape(key) + r'\b', normalized):
                            logger.info(f"Word boundary match: '{key}' in '{normalized}' -> {section}")
                            return section
                    # 如果是长词，使用更严格的匹配
                    elif normalized.startswith(key):
                        logger.info(f"Prefix match: '{key}' in '{normalized}' -> {section}")
                        return section
            return None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            original_line = line
            normalized = normalize_line(line)
            logger.info(f"Processing line: '{line}' -> normalized: '{normalized}'")

            # 检查是否是结束章节
            if any(stop in normalized for stop in stop_sections):
                logger.info(f"Found stop section: {normalized}")
                break

            # 如果看起来像章节标题，尝试匹配
            if is_section_header(line):
                matched_section = find_matching_section(normalized)
                if matched_section:
                    # 保存之前的章节内容
                    if current_section and current_content:
                        content = '\n'.join(current_content).strip()
                        if content:  # 只保存非空内容
                            sections[current_section] = content
                            logger.info(f"Saved content for section {current_section}: {content[:50]}...")
                    current_section = matched_section
                    current_content = []
                    logger.info(f"Starting new section: {matched_section}")
                elif current_section:
                    current_content.append(original_line)
                    logger.info(f"Added line to section {current_section}: {original_line[:50]}...")
            elif current_section:
                current_content.append(original_line)
                logger.info(f"Added line to section {current_section}: {original_line[:50]}...")

        # 保存最后一个章节
        if current_section and current_content:
            content = '\n'.join(current_content).strip()
            if content:  # 只保存非空内容
                sections[current_section] = content
                logger.info(f"Saved content for final section {current_section}: {content[:50]}...")

        logger.info(f"Final sections found: {list(sections.keys())}")
        return sections

if __name__ == "__main__":
    import asyncio

    async def main():
        agent = BlogGenerationAgent()
        pdf_path = "/home/dongpeijie/workspace/LLMToolkit/difypaper/sent/2502_08235/2502_08235.pdf"
        blog_post = await agent.generate_blog(pdf_path)
        output_dir = Path("./output_md")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{blog_post.title.replace(' ', '_')}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {blog_post.title}\n\n{blog_post.content}")
        print(f"\n博客内容已保存到: {output_file}\n")

    asyncio.run(main())
