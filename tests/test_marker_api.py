import os
import pytest
import requests
from PIL import Image
import io
import base64
from unittest.mock import patch, MagicMock
from paper2blog.utils import extract_content_from_pdf

# Create a 100x100 red test image and encode it as base64
def create_test_image():
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return base64.b64encode(img_bytes.getvalue()).decode('utf-8')

MOCK_RESPONSE = {
    "text": "Sample extracted text",
    "images": [
        {
            "data": create_test_image(),
            "format": "png",
            "bbox": [100, 100, 200, 200],
            "page": 1
        }
    ],
    "tables": [
        {
            "data": [
                ["Header1", "Header2", "Header3"],
                ["Data1", "Data2", "Data3"],
                ["Data4", "Data5", "Data6"]
            ],
            "page": 1,
            "bbox": [50, 50, 300, 100]
        }
    ]
}

@pytest.fixture
def mock_marker_client():
    """Create a mock marker client"""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = MOCK_RESPONSE
        mock_post.return_value.status_code = 200
        yield mock_post

@pytest.mark.asyncio
async def test_marker_extraction(mock_marker_client, tmp_path):
    """Test PDF content extraction using marker"""
    # Create a sample PDF content
    pdf_content = b"Sample PDF content"
    
    # Create tmp directory
    os.makedirs("./tmp", exist_ok=True)
    
    try:
        # Extract content
        text_content, images, tables = extract_content_from_pdf(pdf_content)
        
        # Check if marker API was called correctly
        mock_marker_client.assert_called_once()
        args, kwargs = mock_marker_client.call_args
        assert 'files' in kwargs
        
        # Verify extracted content
        assert isinstance(text_content, str)
        assert text_content == "Sample extracted text"
        
        # Verify images
        assert len(images) > 0
        for img in images:
            assert img.caption is not None
            assert img.url is not None
            assert img.markdown is not None
            assert os.path.exists(img.url)
            
        # Verify tables
        assert len(tables) > 0
        assert len(tables[0].columns) == 3  # Three columns in mock data
        assert len(tables[0].index) == 2    # Two rows of data (excluding header)
        assert list(tables[0].columns) == ["Header1", "Header2", "Header3"]
        assert list(tables[0].iloc[0]) == ["Data1", "Data2", "Data3"]
    
    finally:
        # Cleanup
        for img in images:
            if os.path.exists(img.url):
                os.remove(img.url)
        if os.path.exists("./tmp"):
            os.rmdir("./tmp")

@pytest.mark.asyncio
async def test_marker_error_handling():
    """Test error handling when marker server is unavailable"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError
        
        # Should handle error gracefully
        text_content, images, tables = extract_content_from_pdf(b"Sample PDF")
        assert text_content == ""
        assert len(images) == 0
        assert len(tables) == 0

@pytest.mark.asyncio
async def test_marker_invalid_response():
    """Test handling of invalid response from marker"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"invalid": "response"}
        mock_post.return_value.status_code = 200
        
        # Should handle invalid response gracefully
        text_content, images, tables = extract_content_from_pdf(b"Sample PDF")
        assert text_content == ""
        assert len(images) == 0
        assert len(tables) == 0
