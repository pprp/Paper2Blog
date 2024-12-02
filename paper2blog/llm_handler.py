import os
from typing import List, Dict
from openai import AsyncOpenAI
from .models import ImageInfo


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

    async def generate_blog(
        self, text_content: str, language: str, images: List[ImageInfo]
    ) -> Dict:
        try:
            # Set language-specific instructions with advanced prompting
            lang_instructions = {
                "zh": {
                    "system_role": """你是一位在顶级学术期刊发表过多篇论文的资深研究员，同时也是一位成功的科技博主，拥有超过10万读者。
你擅长将复杂的学术论文转化为通俗易懂的技术博客，特别专注于：
1. 深入浅出地解释复杂的技术概念
2. 用生动的类比和实例说明抽象理论
3. 准确把握论文的技术创新点
4. 清晰展示方法论和实验设计

你的写作风格：
- 保持学术严谨性的同时注重可读性
- 善于用故事化的方式展示技术发展过程
- 擅长用图表和可视化辅助解释
- 注重突出实际应用价值""",
                    "style_guide": """
                    高质量技术博客的要求：
                    1. 结构清晰：
                       - 开篇点明论文要解决的核心问题
                       - 主体部分循序渐进地展开技术方案
                       - 结尾总结技术贡献和实际应用

                    2. 技术准确性：
                       - 准确使用专业术语，首次出现时附带解释
                       - 数学公式要配有直观解释
                       - 算法流程要分步骤详细说明
                       - 关键参数要说明选择原因

                    3. 可读性要求：
                       - 使用清晰的中文表达专业概念
                       - 通过类比简化复杂概念
                       - 适当使用图表辅助理解
                       - 突出技术创新点和实际价值

                    4. 图片处理：
                       - 每张图片前要有相关文字铺垫
                       - 图片说明要简洁但信息完整
                       - 确保图片与文字的逻辑关联
                    """,
                },
                "en": {
                    "system_role": """You are a distinguished researcher with multiple publications in top-tier academic journals and a successful tech blogger with over 100,000 readers.
You excel at transforming complex academic papers into accessible technical blog posts, with expertise in:
1. Breaking down complex technical concepts
2. Illustrating abstract theories with vivid analogies
3. Identifying and highlighting technical innovations
4. Clearly presenting methodology and experimental design

Your writing style:
- Maintains academic rigor while ensuring readability
- Uses storytelling to present technical developments
- Leverages diagrams and visualizations effectively
- Emphasizes practical applications""",
                    "style_guide": """
                    Requirements for High-Quality Technical Blogs:
                    1. Clear Structure:
                       - Begin by stating the core problem
                       - Present technical solution progressively
                       - Conclude with contributions and applications

                    2. Technical Accuracy:
                       - Use precise terminology with definitions
                       - Accompany formulas with intuitive explanations
                       - Break down algorithms step-by-step
                       - Justify parameter choices

                    3. Readability:
                       - Express complex concepts clearly
                       - Use analogies to simplify complexity
                       - Incorporate visual aids effectively
                       - Highlight innovations and practical value

                    4. Image Integration:
                       - Introduce context before each image
                       - Provide concise but complete captions
                       - Ensure logical text-image connection
                    """,
                },
            }

            # Use English if language not specified or not supported
            lang = "zh" if language.lower() in ["zh", "chinese", "中文"] else "en"
            curr_lang = lang_instructions[lang]

            # Step 1: Technical Analysis with Chain-of-Thought
            analysis_messages = [
                {"role": "system", "content": curr_lang["system_role"]},
                {
                    "role": "user",
                    "content": f"""
                {curr_lang["style_guide"]}

                Let's analyze this academic paper step by step:

                Step 1: Identify the core problem and motivation
                Step 2: Extract key methodological innovations
                Step 3: Analyze the technical approach in detail
                Step 4: Examine experimental design and validation
                Step 5: Evaluate practical implications

                For each step, think through:
                1. What makes this aspect significant?
                2. How does it advance the field?
                3. What are the practical applications?
                4. How can we explain this to a technical audience?

                Paper content:
                {text_content}

                Provide a detailed analysis following these steps. For each point, explain your reasoning.""",
                },
            ]
            technical_analysis = await self._generate_completion(analysis_messages)

            # Step 2: Create Methodology-Focused Outline with Examples
            outline_messages = [
                {"role": "system", "content": curr_lang["system_role"]},
                {
                    "role": "user",
                    "content": f"""
                {curr_lang["style_guide"]}

                Based on our technical analysis:
                {technical_analysis}

                Create a detailed blog outline that follows this proven structure:

                Example High-Impact Technical Blog Structure:
                1. Introduction
                   - Hook: Real-world problem
                   - Context: Current limitations
                   - Paper's solution: Key innovation

                2. Background
                   - Essential concepts
                   - Previous approaches
                   - Technical prerequisites

                3. Core Methodology
                   - Key innovations
                   - Technical approach
                   - Step-by-step breakdown

                4. Implementation Details
                   - Architecture overview
                   - Critical components
                   - Key algorithms

                5. Experimental Validation
                   - Setup and parameters
                   - Results analysis
                   - Performance insights

                6. Practical Applications
                   - Real-world usage
                   - Implementation considerations
                   - Future directions

                7. Technical Insights
                   - Key takeaways
                   - Design decisions
                   - Engineering trade-offs

                Create an outline following this structure, adapting it to our paper's specific content.""",
                },
            ]
            outline = await self._generate_completion(outline_messages)

            # Step 3: Generate Detailed Technical Content with Storytelling
            content_messages = [
                {"role": "system", "content": curr_lang["system_role"]},
                {
                    "role": "user",
                    "content": f"""
                {curr_lang["style_guide"]}

                Create a comprehensive technical blog post following our outline:
                {outline}

                Technical Analysis:
                {technical_analysis}

                Available Images:
                {self._format_images(images)}

                Follow these expert technical writing principles:
                1. Progressive Disclosure
                   - Start with high-level concepts
                   - Gradually introduce technical details
                   - Build up to complex implementations

                2. Concrete Examples
                   - Use real-world analogies
                   - Provide code snippets where relevant
                   - Include numerical examples

                3. Visual Storytelling
                   - Reference diagrams effectively
                   - Use images to support concepts
                   - Create clear visual flow

                4. Technical Depth
                   - Explain key algorithms thoroughly
                   - Justify design decisions
                   - Discuss trade-offs

                5. Practical Focus
                   - Emphasize real-world applications
                   - Discuss implementation considerations
                   - Address common challenges

                Paper content:
                {text_content}""",
                },
            ]
            blog_content = await self._generate_completion(content_messages)

            # Step 4: Final Review with Quality Checklist
            review_messages = [
                {"role": "system", "content": curr_lang["system_role"]},
                {
                    "role": "user",
                    "content": f"""
                {curr_lang["style_guide"]}

                Review and enhance this technical blog post using this quality checklist:

                Technical Accuracy:
                - [ ] Core concepts explained correctly
                - [ ] Mathematical formulas are accurate
                - [ ] Algorithms properly described
                - [ ] Parameters and setup clear

                Clarity and Flow:
                - [ ] Logical progression of ideas
                - [ ] Complex concepts broken down
                - [ ] Clear transitions between sections
                - [ ] Consistent terminology

                Visual Integration:
                - [ ] Images properly referenced
                - [ ] Diagrams support the text
                - [ ] Figure captions are informative
                - [ ] Visual flow is logical

                Practical Value:
                - [ ] Real-world applications clear
                - [ ] Implementation guidance provided
                - [ ] Limitations discussed
                - [ ] Future directions identified

                Current blog post:
                {blog_content}

                Enhance the content ensuring all checklist items are addressed.""",
                },
            ]
            final_content = await self._generate_completion(review_messages)

            # Extract title and summary
            lines = final_content.split("\n")
            title = next(
                (line.replace("# ", "") for line in lines if line.startswith("# ")),
                "Untitled",
            )

            # Extract summary
            summary_start = final_content.find(
                "## Summary" if lang == "en" else "## 总结"
            )
            summary = "No summary available" if lang == "en" else "暂无总结"
            if summary_start != -1:
                summary_end = final_content.find("##", summary_start + 1)
                if summary_end != -1:
                    summary = final_content[summary_start:summary_end].strip()
                else:
                    summary = final_content[summary_start:].strip()

            return {
                "title": title,
                "content": final_content,
                "summary": summary,
                "tags": [],
            }

        except Exception as e:
            print(f"Error in LLMHandler: {str(e)}")
            raise Exception(f"Failed to generate blog content: {str(e)}")

    async def _save_pdf_to_tmp(self, pdf_bytes: bytes, filename: str) -> str:
        tmp_dir = "./tmp/uploaded_files"
        os.makedirs(tmp_dir, exist_ok=True)
        file_path = os.path.join(tmp_dir, filename)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        return file_path

    async def process_pdf(
        self, pdf_bytes: bytes, filename: str, target_language: str = "en"
    ):
        pdf_path = await self._save_pdf_to_tmp(pdf_bytes, filename)
        return await self.paper_converter.convert_from_pdf(pdf_path, target_language)

    def _format_images(self, images: List[ImageInfo]) -> str:
        formatted_images = []
        for idx, img in enumerate(images, 1):
            formatted_images.append(
                f"Figure {idx}: {img.caption}\n"
                f"Use exactly this markdown to insert the image: ![{img.caption}]({img.markdown})"
            )
        return "\n\n".join(formatted_images)
