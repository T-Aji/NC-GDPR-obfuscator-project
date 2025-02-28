from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="obfuscator",  
    version="0.1.0",  
    author="Tolu Ajibade",  
    description="A library to obfuscate PII in files stored in S3.",  
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",  
    packages=find_packages(where="src"),  
    package_dir={"": "src"},  
    install_requires=requirements,  
    python_requires=">=3.7",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "obfuscator=src.main:obfuscator",  # CLI entry point
        ],
    },
)