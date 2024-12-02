from pydantic import BaseModel
from typing import List, Optional

class ImageInfo(BaseModel):
    caption: str
    url: str
    markdown: str

class ConversionResponse(BaseModel):
    title: str
    content: str
    language: str
    images: List[ImageInfo]
    summary: str
    tags: List[str]
    error: Optional[str] = None
