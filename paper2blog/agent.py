import os
import re
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
from openai import AsyncOpenAI
from paper2blog.model_types import ImageInfo, BlogPost
from paper2blog.utils import extract_content_from_pdf
from paper2blog.llm_handler import LLMHandler


class BlogGenerationAgent:
    def __init__(self, api_key: Optional[str] = None, temperature: float = 0.7):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供OpenAI API密钥")

        self.client = AsyncOpenAI(api_key=self.api_key, base_url=os.getenv("OPENAI_API_BASE"))
        self.temperature = temperature
        self.llm_handler = LLMHandler()

    async def generate_outline(self, text: str) -> str:
        outline_prompt = '''你是一位专业的技术博主，请基于以下论文内容生成一个详细的博客大纲。使用中文回复。

请按照以下结构组织大纲，并为每个部分添加简短说明：

1. 开篇导读
   - 论文要解决的核心问题
   - 研究的重要性和实际应用价值
   - 主要贡献点概述

2. 研究背景与动机
   - 领域现状和挑战
   - 已有解决方案的局限性
   - 研究切入点

3. 技术方案详解
   - 核心思想和创新点
   - 具体实现方法
   - 关键技术组件
   - 算法或模型设计

4. 实验验证与分析
   - 实验设置和评估指标
   - 核心实验结果
   - 消融实验分析
   - 案例分析和讨论

5. 总结与展望
   - 主要结论
   - 实际应用建议
   - 未来研究方向

论文内容：
{text}

请生成一个清晰的大纲，并在每个部分后添加简短说明，说明该部分将要讨论的主要内容。'''

        response = await self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=[{"role": "user", "content": outline_prompt}],
            temperature=self.temperature,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

    async def generate_blog_section(self, text: str, section_title: str, context: str, style_guide: str) -> str:
        prompt = f"""你是一位专业的技术博主，擅长将学术论文转化为通俗易懂的技术博客。请用中文进行回复。

当前章节：{section_title}

请将以下论文片段转换为博客章节，遵循以下要求：

1. **内容要求**：
   - 内容要详实，深入浅出
   - 保持逻辑流畅，段落之间要有明确的过渡
   - 专业术语首次出现时要有解释
   - 确保与章节主题紧密相关

2. **风格要求**：
   - 使用{style_guide}的语调
   - 保持自然、人性化的表达
   - 适当使用类比和举例来解释复杂概念
   - 确保与上下文的连贯性

3. **结构要求**：
   - 每个段落开头要有清晰的主题句
   - 段落之间要有适当的过渡语
   - 在章节末尾要有简短的小结
   - 适当添加分点说明，提高可读性

4. **上下文信息**：
{context}

论文片段：
{text}

请生成连贯、专业且易于理解的博客章节："""

        response = await self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=3000
        )
        return response.choices[0].message.content

    async def generate_blog_with_agent(self, text_chunks: List[str], image_info: List[ImageInfo]) -> str:
        # 首先生成大纲
        full_text = " ".join(text_chunks)
        outline = await self.generate_outline(full_text)
        print("生成的大纲：\n", outline)
        
        # 让用户确认或修改大纲
        print("\n请确认大纲是否合适，如需修改请直接修改。按回车继续...")
        input()
        
        blog_sections = []
        context = "这是一篇技术博客的开始。"
        
        # 根据大纲组织内容
        current_section = ""
        for chunk in text_chunks:
            # 检测当前chunk最适合哪个章节
            section_prompt = f"""基于以下大纲和文本片段，判断这段内容最适合放在哪个章节中？只需返回章节标题。

大纲：
{outline}

文本片段：
{chunk}

请返回最适合的章节标题："""
            
            response = await self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                messages=[{"role": "user", "content": section_prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            section_title = response.choices[0].message.content.strip()
            
            if section_title != current_section:
                current_section = section_title
                blog_sections.append(f"\n## {current_section}\n")
            
            content = await self.generate_blog_section(
                chunk,
                current_section,
                context,
                "专业但平易近人"
            )
            blog_sections.append(content)
            context = f"前文讨论了{current_section}的内容。"
        
        # 合并所有章节
        blog_content = "\n\n".join(blog_sections)
        
        # 后处理优化
        final_blog = await self.post_process_blog(blog_content)
        
        return final_blog

    async def post_process_blog(self, blog_content: str) -> str:
        post_process_prompt = f"""请对以下技术博客内容进行优化，重点关注：

1. 检查并增强段落之间的连贯性
2. 统一文章的语气和专业术语使用
3. 确保逻辑转换自然流畅
4. 添加必要的过渡语句
5. 确保专业术语的解释完整且一致
6. 优化段落结构，使文章更易阅读
7. 检查并完善各个章节之间的关联

博客内容：
{blog_content}

请返回优化后的博客内容。"""

        response = await self.client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=[{"role": "user", "content": post_process_prompt}],
            temperature=self.temperature,
            max_tokens=4000
        )
        return response.choices[0].message.content

    async def generate_blog(self, pdf_path: str, target_language: str = "zh") -> BlogPost:
        print(f"从PDF提取内容: {pdf_path}")
        text_content, images = await extract_content_from_pdf(pdf_path)
        text_chunks = self._split_text(text_content)

        print("生成博客内容")
        full_blog_text = await self.generate_blog_with_agent(text_chunks, images)

        for img in images:
            placeholder = f"[Figure {img.caption.split(':')[0] if ':' in img.caption else img.caption}]"
            full_blog_text = full_blog_text.replace(placeholder, img.markdown)

        print("生成博客标题")
        title = await self.llm_handler.translate_title(text_content, target_language)

        return BlogPost(title=title, content=full_blog_text)

    def _split_text(self, text: str, n_splits: int = 4) -> List[str]:
        stop_sections = {'references', 'appendix', 'acknowledgements', 'acknowledgments', 'bibliography'}
        
        lines = text.split("\n")
        main_content_lines = []
        
        for line in lines:
            line_lower = line.strip().lower()
            if any(stop in line_lower for stop in stop_sections):
                break
            if line.strip():
                main_content_lines.append(line)
                
        main_content = "\n".join(main_content_lines)
        
        sections = []
        total_length = len(main_content)
        chunk_size = total_length // n_splits
        
        current_pos = 0
        while current_pos < total_length:
            next_pos = min(current_pos + chunk_size, total_length)
            if next_pos < total_length:
                paragraph_end = main_content.find('\n\n', next_pos - 100, next_pos + 100)
                if paragraph_end != -1:
                    next_pos = paragraph_end
                else:
                    sentence_end = main_content.find('.', next_pos - 50, next_pos + 50)
                    if sentence_end != -1:
                        next_pos = sentence_end + 1
            
            chunk = main_content[current_pos:next_pos].strip()
            if chunk:
                sections.append(chunk)
            current_pos = next_pos
        
        cleaned_sections = [self._clean_chunk(section) for section in sections if self._clean_chunk(section)]
        
        return cleaned_sections

    def _clean_chunk(self, text: str) -> str:
        text = ' '.join(text.split())
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        text = re.sub(r'([.,!?;:-])\1+', r'\1', text)
        text = re.sub(r'([.,!?;:-])(\w)', r'\1 \2', text)
        text = re.sub(r'http\S+|www\S+|\[\d+\]|\(\d+\)', '', text)
        return text.strip()

if __name__ == "__main__":
    agent = BlogGenerationAgent()
    pdf_path = "/home/dongpeijie/workspace/LLMToolkit/difypaper/sent/2502_08235/2502_08235.pdf"
    blog_post = asyncio.run(agent.generate_blog(pdf_path))
    output_dir = Path("./output_md")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{blog_post.title.replace(' ', '_')}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {blog_post.title}\n\n{blog_post.content}")
    print(f"\n博客内容已保存到: {output_file}\n")
