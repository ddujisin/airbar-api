"""AirBar API setup configuration."""
from setuptools import setup, find_packages

setup(
    name="airbar-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "prisma>=0.11.0",
        "pydantic>=2.5.0",
        "websockets>=12.0",
        "python-multipart>=0.0.6",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "httpx>=0.25.1",
    ],
    extras_require={
        "dev": [
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "pytest-cov>=4.1.0",
        ]
    },
    python_requires=">=3.12",
)
