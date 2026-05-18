"""Setup for Ableton CLI Harness."""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("README.md") as f:
    long_description = f.read()

setup(
    name="cli-ableton",
    version="0.1.0",
    description="Command-line control for Ableton Live through AbletonOSC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Skyxswl",
    url="https://github.com/Skyxswl/cli-ableton",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ableton=cli_anything.ableton.ableton_cli:cli",
            "cli-ableton=cli_anything.ableton.ableton_cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Audio",
    ],
    python_requires=">=3.10",
)
