from setuptools import setup, find_packages

setup(
    name="ai-safety-guardrails-sdk",
    version="0.1.0",
    description="Lightweight SDK for wrapping LLM calls with safety guards",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0"],
        "full": ["jsonschema>=4.0", "openai>=1.0.0"]
    }
)
