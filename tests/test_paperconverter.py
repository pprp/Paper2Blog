import asyncio
from paper2blog.converter import PaperConverter
from paper2blog.models import ConversionResponse


async def test_convert_from_pdf():
    converter = PaperConverter()

    result = await converter.convert_from_pdf(
        "/Users/peyton/Workspace/Paper2Blog/tests/data/sample.pdf", target_language="de"
    )

    assert isinstance(result, ConversionResponse)
    assert result.language == "de"
    assert result.title != ""
    assert result.content != ""
    assert result.summary != ""
    assert len(result.images) > 0


if __name__ == "__main__":
    asyncio.run(test_convert_from_pdf())
