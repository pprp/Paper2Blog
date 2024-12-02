import asyncio
from paper2blog.converter import PaperConverter
from paper2blog.models import ConversionResponse


async def test_convert_from_pdf():
    converter = PaperConverter()

    result = await converter.convert_from_pdf(
        "/Users/peyton/Workspace/Paper2Blog/tests/data/sample.pdf", target_language="de"
    )

    breakpoint()


if __name__ == "__main__":
    asyncio.run(test_convert_from_pdf())
