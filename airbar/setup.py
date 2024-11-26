from setuptools import setup, find_packages

setup(
    name="airbar",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "prisma",
        "pydantic",
        "pytest",
        "pytest-asyncio",
        "pytz"
    ],
)
