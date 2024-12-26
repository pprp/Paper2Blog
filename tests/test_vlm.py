import pytest
import base64
from paper2blog.vlm_handler import VLMHandler
from PIL import Image
import io

@pytest.fixture
def vlm_handler():
    return VLMHandler()

@pytest.fixture
def sample_image_data():
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

@pytest.mark.asyncio
async def test_generate_caption(vlm_handler, sample_image_data):
    # Test data
    text_data = "This is a test paper about image recognition"
    
    # Call generate_caption
    caption = await vlm_handler.generate_caption(text_data, sample_image_data)
    
    # Verify response
    assert isinstance(caption, str)
    assert len(caption) > 0

@pytest.mark.asyncio
async def test_generate_caption_invalid_image():
    handler = VLMHandler()
    invalid_image_data = b"invalid image data"
    
    with pytest.raises(Exception):
        await handler.generate_caption("test text", invalid_image_data)

@pytest.mark.asyncio
async def test_generate_caption_empty_text(vlm_handler, sample_image_data):
    caption = await vlm_handler.generate_caption("", sample_image_data)
    assert isinstance(caption, str)
    assert len(caption) > 0

@pytest.mark.asyncio
async def test_api_error_handling(vlm_handler):
    # Test with invalid API key
    vlm_handler.api_key = "invalid_key"
    
    with pytest.raises(Exception) as exc_info:
        await vlm_handler.generate_caption("test", b"test")
    assert "API request failed" in str(exc_info.value)
