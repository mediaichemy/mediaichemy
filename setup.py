from setuptools import setup, find_packages

setup(
    name="mediaichemy",
    version="0.1.0b1",
    description="A Python library for AI powered multimedia content creation 🧪",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pedro Blaya Luz",
    author_email="blaya.luz@gmail.com",
    url="https://github.com/pedroblayaluz/mediaichemy",
    license="MIT",
    packages=find_packages(exclude=["tests*", "htmlcov*"]),
    include_package_data=True,
    install_requires=[
        "elevenlabs==1.56.0",
        "httpx==0.28.1",
        "ipython==9.0.2",
        "ipywidgets==8.1.5",
        "langcodes==3.5.0",
        "matplotlib==3.10.1",
        "mutagen==1.47.0",
        "Pillow==11.1.0",
        "pydantic==2.11.3",
        "pysubs2==1.8.0",
        "pytest==8.3.5",
        "requests==2.32.3",
        "runware==0.4.8",
        "setuptools==78.1.0",
        "toml==0.10.2",
        "yt-dlp==2025.3.31",
        "youtube-transcript-api==1.0.3"
    ],
    extras_require={
        "tests": [
            "pytest==8.3.5",
            "pytest-asyncio==0.26.0",
            "pytest-cov==6.1.1",
            "flake8==6.1.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "mediaichemy-cli=mediaichemy.cli:main",
        ],
    },
)
