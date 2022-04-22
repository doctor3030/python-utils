from setuptools import setup, find_packages
import pathlib

# # The directory containing this file
# ROOOT = pathlib.Path(__file__).parent
#
# # The text of the README file
# README = (ROOOT / "README.md").read_text()

setup(
    name='python-utils',
    version='0.0.1',
    url='https://github.com/doctor3030/python-utils',
    license='MIT',
    author='Dmitry Amanov',
    author_email='',
    description='python utilities',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
)
