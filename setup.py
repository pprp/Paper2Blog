from setuptools import setup, find_packages

setup(
    name="paper2blog",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "pandas>=1.3.0",
        "Pillow>=8.3.0",
        "numpy>=1.21.0",
        "openai>=0.27.0",
        "pydantic>=1.8.0",
        "python-multipart>=0.0.5",
        "tabulate>=0.8.9",  # For DataFrame to markdown conversion
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-asyncio>=0.16.0",
            "black>=21.7b0",
            "isort>=5.9.3",
            "flake8>=3.9.2",
        ],
    },
    python_requires=">=3.8",
    author="Peyton",
    author_email="peyton@example.com",
    description="An AI-powered tool to convert academic papers to blog posts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/paper2blog",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
