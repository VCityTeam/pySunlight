#!/bin/bash
# This bash is used to remove swig wrapper from the current folder.

rm -rf build/
rm -rf __pycache__/
rm *_wrap.cxx
rm *.so
rm pySunlight.py