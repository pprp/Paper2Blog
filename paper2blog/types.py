from typing import List, Optional
from pydantic import BaseModel

class ImageInfo(BaseModel):
    caption: str
    url: str
    markdown: str

class BlogPost(BaseModel):
    title: str
    content: str
    summary: str

class ConversionResponse(BaseModel):
    title: Optional[str] = ""
    content: Optional[str] = ""
    summary: Optional[str] = ""
    language: str
    images: List[ImageInfo] = []
    error: Optional[str] = None
    tags: List[str] = []
