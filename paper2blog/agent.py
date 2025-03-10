from langchain import OpenAI
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, Dict


# Mock functions for other parts
def mock_parse_pdf(pdf_path: str) -> tuple[List[str], List[Dict[str, str]]]:
    """模拟 PDF 解析，返回分块文本和 figure 数据。

    Args:
        pdf_path (str): PDF 文件路径。

    Returns:
        tuple: (text_chunks, figure_data)，其中 text_chunks 是文本块列表，figure_data 是包含 figure_id 和 caption 的字典列表。
    """
    text = (
        "This is a mock text from the PDF. It contains multiple sections about LLMs. "
        "Figure 1 shows the model architecture. The next section discusses training."
    )
    # 按 100 字符分块，模拟论文分段
    text_chunks = [text[i : i + 100] for i in range(0, len(text), 100)]
    figure_data = [{"figure_id": "1", "caption": "Model Architecture"}]
    return text_chunks, figure_data


def mock_upload_images_to_github_pages(image_paths: List[str]) -> Dict[str, str]:
    """模拟图片上传，返回图片路径到 URL 的映射。

    Args:
        image_paths (List[str]): 图片路径列表。

    Returns:
        Dict[str, str]: 图片路径到 URL 的映射。
    """
    return {path: f"https://example.com/{path}" for path in image_paths}


# 初始化 LLM
llm = OpenAI(temperature=0.7, max_tokens=1000)  # 设置 max_tokens 确保输出足够长

# 定义生成博客段落的 Prompt 模板
blog_section_prompt = PromptTemplate(
    input_variables=["text", "context", "style_guide"],
    template="""You are a skilled technical blog writer tasked with converting a section of a computer science paper into an engaging blog post for enthusiasts. Follow these instructions:

1. **Content**: Transform the given paper section into a detailed blog post, at least 300 words. Explain core concepts clearly, using simple language and relatable examples (e.g., compare technical ideas to everyday scenarios).
2. **Style**: Write in a {style_guide} tone, maintaining a natural, human-like flow. Avoid overly academic jargon unless explained.
3. **Figures**: If the text mentions figures (e.g., 'Figure 1'), insert [Figure X] as a placeholder at the appropriate point.
4. **Context**: Use the previous context to ensure logical flow and avoid repetition: {context}

Paper section:
{text}

Blog post:""",
)

# 创建 LLMChain 用于生成博客段落
blog_section_chain = LLMChain(llm=llm, prompt=blog_section_prompt)

# 定义 Tool，封装生成博客段落的功能
generate_section_tool = Tool(
    name="Generate Blog Section",
    func=lambda inputs: blog_section_chain.run(
        {
            "text": inputs["text"],
            "context": inputs["context"],
            "style_guide": inputs.get("style_guide", "friendly and conversational"),
        }
    ),
    description="Generates a detailed blog section from a paper excerpt, ensuring clarity and engagement.",
)

# 初始化 Agent
agent = initialize_agent(
    tools=[generate_section_tool],
    llm=llm,
    agent_type="zero-shot-react-description",  # 使用简单的反应式 Agent
    verbose=True,  # 输出调试信息
)


# 使用 Agent 分段生成博客内容
def generate_blog_with_agent(
    text_chunks: List[str], figure_data: List[Dict[str, str]]
) -> str:
    """使用 Agent 分段生成博客内容。

    Args:
        text_chunks (List[str]): 分块的论文文本。
        figure_data (List[Dict[str, str]]): 包含 figure_id 和 caption 的数据。

    Returns:
        str: 完整的博客内容。
    """
    blog_sections = []
    previous_context = (
        "This blog introduces a paper on large language models (LLMs)."  # 初始上下文
    )

    for i, chunk in enumerate(text_chunks):
        print(f"Generating section {i+1}...")
        # 构建 Agent 输入
        agent_input = {
            "text": chunk,
            "context": previous_context,
            "style_guide": "friendly and conversational",  # 可动态调整
        }

        # 调用 Agent 生成当前段落
        section = agent.run(
            f"Generate a blog section from the following input: {agent_input}"
        )
        blog_sections.append(section)

        # 更新上下文：提取当前段落的核心信息，避免过长
        previous_context = (
            f"Previous section discussed: {section[:100]}..."
            if len(section) > 100
            else section
        )

    return "\n\n".join(blog_sections)  # 用换行分隔段落，便于阅读


# 主函数，整合 Agent 生成博客
def generate_blog(pdf_path: str) -> str:
    """生成完整的图文混排博客。

    Args:
        pdf_path (str): PDF 文件路径。

    Returns:
        str: 最终的博客内容。
    """
    # Mock PDF 解析
    text_chunks, figure_data = mock_parse_pdf(pdf_path)

    # 使用 Agent 生成博客内容
    full_blog_text = generate_blog_with_agent(text_chunks, figure_data)

    # Mock 图片上传并替换 figure ID 占位符
    image_paths = [f"image_{fig['figure_id']}.png" for fig in figure_data]
    image_urls = mock_upload_images_to_github_pages(image_paths)
    for fig in figure_data:
        fig["url"] = image_urls[f"image_{fig['figure_id']}.png"]
        full_blog_text = full_blog_text.replace(
            f"[Figure {fig['figure_id']}]", f"![{fig['caption']}]({fig['url']})"
        )

    return full_blog_text


# 示例调用
if __name__ == "__main__":
    pdf_path = "path/to/your/pdf.pdf"
    blog_content = generate_blog(pdf_path)
    print("\nGenerated Blog Content:\n")
    print(blog_content)
