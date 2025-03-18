from setuptools import setup, find_packages

setup(
    name="françoise",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author="Colin Teal",
    author_email="the30yearswar@hotmail.com",
    description="A French language pen pal powered by ollama.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/crteal/françoise",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
