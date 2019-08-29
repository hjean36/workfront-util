from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

s = setup(
    name="workfrontutil",
    version="0.0.5",
    license="MIT",
    description="Python Wrapper for the Workfront API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hjean36/workfront-util",
    packages=['cli', 'services', 'tests'],
    install_requires=[],
    python_requires = ">= 3.7",
    author="Harley Jean",
    author_email="hjean35@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "workfrontutil = cli.workfrontcli:main"
        ]
    }        
)