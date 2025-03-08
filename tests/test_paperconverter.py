import asyncio
from paper2blog.converter import PaperConverter
from paper2blog.types import ConversionResponse


async def test_convert_from_pdf():
    converter = PaperConverter()

    result = await converter.convert_from_pdf(
        "/home/dongpeijie/workspace/Paper2Blog/tests/data/sample.pdf", target_language="de"
    )

    breakpoint()


if __name__ == "__main__":
    asyncio.run(test_convert_from_pdf())
