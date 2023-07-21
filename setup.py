# -- coding: utf-8 --
from setuptools import setup, find_packages

requirements = ('py3dtilers @ git+https://github.com/VCityTeam/py3dtilers')

dev_requirements = (
    'flake8',
    'autopep8',
    'pdoc3'
)

setup(
    name='pySunlight',
    version='0.2',
    description="Python module for computing Sunlight with 3DTiles",
    url='https://github.com/VCityTeam/pySunlight',
    author='Université de Lyon',
    author_email='contact@liris.cnrs.fr',
    license='Apache License Version 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    test_suite="tests",
    entry_points={
        'console_scripts': ['sunlight=sunlight.py:main'],
    }
)
