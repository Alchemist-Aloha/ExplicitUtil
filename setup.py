from setuptools import setup

setup(
    name="explicit_util",
    version="1.0",
    packages=["explicit_util"],
    install_requires=[
        "tqdm",
        "namer",
        "pillow",
    ],
    author="Alchemist-Aloha",
    description="A utility library for managing media files",
    url="https://github.com/Alchemist-Aloha/lust_util",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
)
