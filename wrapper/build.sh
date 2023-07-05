#!/bin/bash
# This bash is used to build and compile a C++ file to a python wrapper using SWIG : https://www.swig.org/.

# Create wrapper code (_wrap.cxx)
swig -c++ -python sunlight.i

# Compile as a shared library (.so)
python3 setup.py build_ext --inplace

# Compilation 
# python3 setup.py build

# Installation on current desktop
# python3 setup.py install