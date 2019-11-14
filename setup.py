"""Installation script."""

from setuptools import setup, find_packages

setup(
    name='districtcooling',
    version='0.1',
    py_modules=find_packages(),
    install_requires=[
        'geopandas',
        'matplotlib',
        'networkx',
        'numpy',
        'pandas',
        'pyomo'
    ])