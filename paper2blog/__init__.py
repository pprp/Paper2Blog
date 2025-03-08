"""
Paper2Blog - Convert academic papers to engaging blog posts

This package provides tools to:
1. Extract content from PDF papers
2. Process and analyze the content
3. Generate blog posts using AI in a one-shot approach
4. Handle images and tables intelligently
"""

__version__ = "0.1.0"

from .converter import PaperConverter
from .types import ConversionResponse, ImageInfo, BlogPost
from .utils import extract_content_from_pdf

__all__ = [
    "PaperConverter",
    "ConversionResponse",
    "ImageInfo",
    "BlogPost",
    "extract_content_from_pdf",
]
