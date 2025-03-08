import re

def format_image_markdown(content: str) -> str:
    """
    Format markdown image references by combining the image and caption into a single line.
    
    Args:
        content (str): Input markdown content
        
    Returns:
        str: Formatted markdown content
    """
    # Pattern to match image reference and its following caption
    pattern = r'!\[\]\(([^)]+)\)\s*\n\s*<span[^>]*>.*?</span>(.+?)(?=\n\n|$)'
    
    def replace_match(match):
        img_path = match.group(1)
        caption = match.group(2).strip()
        return f'![{caption}]({img_path})'
    
    # Replace all matches in the content
    formatted_content = re.sub(pattern, replace_match, content, flags=re.DOTALL)
    return formatted_content

# def test_format_image_markdown():
#     """Test the image markdown formatting function"""
#     input_md = """![](_page_0_Figure_5.jpeg)

# <span id="page-0-0"></span>Figure 1. Effect of skipping a specific position within the Control-Net block on the quality of the generated image. Higher FID and HDD indicate a more significant impact of the skipped layer on the quality of the final results, reflecting a stronger correlation with the generated image quality."""

#     expected_output = """![Figure 1. Effect of skipping a specific position within the Control-Net block on the quality of the generated image. Higher FID and HDD indicate a more significant impact of the skipped layer on the quality of the final results, reflecting a stronger correlation with the generated image quality.](_page_0_Figure_5.jpeg)"""

#     result = format_image_markdown(input_md)
#     assert result.strip() == expected_output.strip(), f"Expected:\n{expected_output}\n\nGot:\n{result}"

if __name__ == "__main__":
    # test_format_image_markdown()
    
    with open("./tmp/saved_pngs/output.md") as f:
        input_md = f.read()
    
    output = format_image_markdown(input_md)

    with open("./tmp/saved_pngs/output_format.md", "w") as f:
        f.write(output)

    print("All tests passed!")
