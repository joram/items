import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="items",
    version="0.0.2",
    author="John Oram",
    author_email="john@oram.ca",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joram/items",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["items"],
    package_data={
        "items": [
            "items/altitude_sports/*",
            "items/mec/*",
            "items/rei/*",
        ]
    },
    package_dir={"items": "items"},
    python_requires=">=3.6",
)
