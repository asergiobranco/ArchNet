from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ArchNet",
    version="0.0.1",
    author="Sergio Branco | The Architech",
    author_email="asergio.branco@gmail.com",
    description="ArchNet is a decentralized network package, to build strong, powerfull and secure applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="archnet.asergiobranco.com",
    include_package_data = True,
    packages=find_packages(),
    package_data={
        '': ['*.md'],
        'html_docs' : ['*'],

    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet"
    ],
)
