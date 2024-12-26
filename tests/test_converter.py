import os
import pytest
import fitz
from PIL import Image
import io
from unittest.mock import patch, AsyncMock
from paper2blog.converter import PaperConverter
from paper2blog.models import ConversionResponse, ImageInfo, BlogPost
from paper2blog.utils import extract_content_from_pdf
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(autouse=True)
def setup_environment():
    """Setup environment variables for testing"""

    # Set default test environment variables
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("OPENAI_API_BASE", "https://api.openai.com/v1")
    os.environ.setdefault("OPENAI_MODEL", "gpt-4")
    yield


@pytest.fixture
def sample_pdf_path():
    """Get path to sample PDF file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "data", "sample.pdf")


@pytest.fixture
def create_test_pdf_with_image(tmp_path):
    """Create a test PDF with an embedded image"""
    # Create a simple test image
    img_size = (300, 200)
    test_image = Image.new("RGB", img_size, color="red")
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Create PDF with the image
    doc = fitz.open()
    page = doc.new_page()
    page.insert_image(rect=(100, 100, 400, 300), stream=img_bytes.getvalue())

    # Add some text
    page.insert_text((50, 50), "Test PDF with image")

    # Save the PDF
    pdf_path = os.path.join(tmp_path, "test_with_image.pdf")
    doc.save(pdf_path)
    doc.close()

    return pdf_path


@pytest.fixture
def mock_llm_handler():
    """Create a mock LLM handler that returns test data"""
    mock_blog_post = BlogPost(
        title="Test Blog Post",
        content="This is a test blog post content",
        summary="Test summary",
    )

    async_mock = AsyncMock()
    async_mock.generate_blog_post.return_value = mock_blog_post
    return async_mock


@pytest.mark.asyncio
async def test_image_extraction(create_test_pdf_with_image):
    """Test extraction of images from PDF"""
    # Read the test PDF
    with open(create_test_pdf_with_image, "rb") as f:
        pdf_content = f.read()

    # Extract content
    text_content, images = extract_content_from_pdf(pdf_content)

    # Verify image extraction
    assert len(images) > 0, "No images were extracted"
    assert all(
        isinstance(img, ImageInfo) for img in images
    ), "Extracted images should be ImageInfo objects"

    breakpoint()

    # Check image properties
    for img in images:
        assert img.caption is not None, "Image should have a caption"
        assert img.url is not None, "Image should have a URL"
        assert img.markdown is not None, "Image should have markdown"
        assert img.markdown.startswith("!["), "Markdown should be in correct format"

        # Verify the image file exists and is valid
        assert os.path.exists(img.url), f"Image file does not exist at {img.url}"
        with Image.open(img.url) as img_file:
            assert img_file.size[0] >= 100, "Image width should be at least 100px"
            assert img_file.size[1] >= 100, "Image height should be at least 100px"


@pytest.mark.asyncio
async def test_image_quality_filtering(create_test_pdf_with_image):
    """Test that low quality images are filtered out"""
    # Create a PDF with a very small, low quality image
    doc = fitz.open()
    page = doc.new_page()

    # Add a small, low quality image
    small_img = Image.new("RGB", (50, 50), color="blue")
    small_img_bytes = io.BytesIO()
    small_img.save(small_img_bytes, format="PNG")
    small_img_bytes.seek(0)

    page.insert_image(rect=(10, 10, 60, 60), stream=small_img_bytes.getvalue())

    # Save the PDF
    pdf_path = os.path.join(
        os.path.dirname(create_test_pdf_with_image), "small_image.pdf"
    )
    doc.save(pdf_path)
    doc.close()

    # Test extraction
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    text_content, images, _ = extract_content_from_pdf(pdf_content)

    # Small image should be filtered out
    assert len(images) == 0, "Small, low quality image should be filtered out"


@pytest.mark.asyncio
async def test_full_conversion_with_images(
    create_test_pdf_with_image, mock_llm_handler
):
    """Test full PDF conversion including image handling"""
    converter = PaperConverter()
    converter.llm_handler = mock_llm_handler

    result = await converter.convert_from_pdf(create_test_pdf_with_image)

    # Check conversion result
    assert isinstance(result, ConversionResponse)
    assert result.error is None, f"Conversion error: {result.error}"
    assert len(result.images) > 0, "No images in conversion result"
    assert result.title == "Test Blog Post", "Incorrect title"
    assert result.content == "This is a test blog post content", "Incorrect content"
    assert result.summary == "Test summary", "Incorrect summary"

    # Check if images are referenced in content
    for img in result.images:
        assert os.path.exists(img.url), f"Image file missing: {img.url}"


@pytest.mark.asyncio
async def test_invalid_image_handling():
    """Test handling of invalid or corrupted images"""
    # Create a PDF with corrupted image data
    doc = fitz.open()
    page = doc.new_page()

    # Add some corrupted "image" data
    corrupt_data = b"Not a valid image"
    try:
        page.insert_image(rect=(100, 100, 200, 200), stream=corrupt_data)
    except:
        # If insertion fails, add some text instead
        page.insert_text((100, 100), "Corrupted image test")

    # Save the PDF
    pdf_path = "./tmp/corrupt_image.pdf"
    doc.save(pdf_path)
    doc.close()

    # Test extraction
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    # Should not raise exception for corrupted images
    text_content, images, _ = extract_content_from_pdf(pdf_content)
    assert len(images) == 0, "Corrupted images should be filtered out"


def test_cleanup_temp_files(create_test_pdf_with_image):
    """Test that temporary image files are handled properly"""
    with open(create_test_pdf_with_image, "rb") as f:
        pdf_content = f.read()

    text_content, images, _ = extract_content_from_pdf(pdf_content)

    # Store image paths
    image_paths = [img.url for img in images]

    # Verify files exist
    for path in image_paths:
        assert os.path.exists(path), f"Image file should exist: {path}"

    # In a real application, you would implement cleanup here
    # For testing, we just verify the files are in the expected temporary location
    for path in image_paths:
        assert path.startswith("./tmp/"), "Image files should be in temporary directory"


@pytest.mark.asyncio
async def test_convert_from_pdf():
    """Test converting PDF to blog post"""
    converter = PaperConverter()

    # Test with a real PDF file
    result = await converter.convert_from_pdf(
        "/home/dongpeijie/workspace/Paper2Blog/tests/data/sample.pdf", target_language="en"
    )

    assert isinstance(result, ConversionResponse)
    assert result.language == "en"
    assert isinstance(result.images, list)
    assert all(isinstance(img, ImageInfo) for img in result.images)
    assert not result.error  # No error should be present
