# -- coding: utf-8 --
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

# Execute CMake command
import subprocess
import os

# # ====================================== Setup Sunlight Compilation and create python module ======================================
# Extending setuptools extension with CMake setup : https://stackoverflow.com/questions/42585210/extending-setuptools-extension-to-use-cmake-in-setup-py
# Setup.py with CMake example : https://github.com/pybind/cmake_example/blob/master/setup.py


class CMakeExtension(Extension):
    def __init__(self, name, sources=[]):
        Extension.__init__(self, name, sources=sources)


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        build_args = ['--config', 'Release']

        # Source and build directories
        source_dir = os.path.abspath(os.path.dirname(__file__))
        build_dir = os.path.join(source_dir, 'build')

        # Create build directory
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        # Execute CMake commands
        subprocess.check_call(['cmake', source_dir], cwd=build_dir)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=build_dir)


# ====================================== Setup Python requirements ======================================
# I do not use the latest release of py3DTilers, becausei t doesn't have the fix to force scipy version.
# The latests scipy version require a more recent numpy version that was incompatible with py3dTilers and py3DTiles. 
requirements = ('py3dtilers @ git+https://github.com/VCityTeam/py3dtilers@ff2cca7b97ee7a63f04c9ffbf7cd1b2054949332')

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

    # Build Sunlight and export as a python module
    ext_modules=[CMakeExtension('pySunlight')],
    cmdclass=dict(build_ext=CMakeBuild),

    # Python requirements
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    test_suite="tests",
    entry_points={
        'console_scripts': ['sunlight=sunlight.py:main'],
    }
)
