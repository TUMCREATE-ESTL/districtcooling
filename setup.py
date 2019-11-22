"""Installation script."""

import setuptools

setuptools.setup(
    name='districtcooling',
    version='0.1.0',
    py_modules=setuptools.find_packages(),
    install_requires=[
        'geopandas',
        'matplotlib',
        'networkx',
        'numpy',
        'pandas',
        'pyomo',
        'shapely',
        'utm'
    ])