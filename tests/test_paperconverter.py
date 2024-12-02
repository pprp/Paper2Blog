from paper2blog.converter import PaperConverter

converter = PaperConverter()

breakpoint()

result = converter.convert_from_pdf(
    "tests/data/sample.pdf",
    target_language="de",
)
