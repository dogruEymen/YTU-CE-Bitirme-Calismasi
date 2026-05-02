# setup.py
from setuptools import setup, find_packages

setup(
    name="ytu-ce-bitirme",
    version="0.1",
    packages=find_packages(include=['database', 'database.*', 'backend', 'backend.*']),
)
