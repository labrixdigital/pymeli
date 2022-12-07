from setuptools import setup, find_packages, Extension
from os import path

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pymeli',
    version='0.1.2',
    description='A nice SDK for Mercado Libre',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/labrixdigital/pymeli',
    author='Ernesto Monroy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='meli',
    packages=find_packages(include=['pymeli']),
    python_requires='>=3.5',
    project_urls={
        'Bug Reports': 'https://github.com/labrixdigital/pymeli/issues',
        'Source': 'https://github.com/labrixdigital/pymeli',
    },
    install_requires = ['requests']
)