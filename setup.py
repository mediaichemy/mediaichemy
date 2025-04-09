from setuptools import setup, find_packages

setup(
    name="mediaichemy",
    version="0.1.0",
    description="A Python Framework for AI-powered media editing and content creation.",
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
        "mutagen==1.47.0",
        "Pillow==11.1.0",
        "pydantic==2.11.3",
        "pysubs2==1.8.0",
        "pytest==8.3.5",
        "requests==2.32.3",
        "runware==0.4.8",
        "setuptools==78.1.0",
        "toml==0.10.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "mediaichemy-cli=mediaichemy.cli:main",
        ],
    },
)
