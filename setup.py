from pathlib import Path

from setuptools import find_packages, setup

PACKAGE_NAME = "ai-safety-guardrails-sdk"

README_PATH = Path(__file__).parent / "README.md"
LONG_DESCRIPTION = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else "AI Safety Guardrails SDK"

setup(
    name=PACKAGE_NAME,
    version="0.2.0",
    description="Enterprise-ready guardrails for LLM and agent safety",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="AI Safety Guardrails Team",
    url="https://github.com/beautifulgownss/ai-safety-guardrails-sdk",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0,<3.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "ruff>=0.4",
            "mypy>=1.7",
            "types-requests",
        ],
        "docs": [
            "mkdocs>=1.5",
            "mkdocs-material>=9.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Documentation": "https://github.com/beautifulgownss/ai-safety-guardrails-sdk/docs",
        "Source": "https://github.com/beautifulgownss/ai-safety-guardrails-sdk",
        "Issues": "https://github.com/beautifulgownss/ai-safety-guardrails-sdk/issues",
    },
)
