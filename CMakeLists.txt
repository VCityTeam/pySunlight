# CMakeLists.txt
cmake_minimum_required(VERSION 3.2)
project(pySunlight LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

# Set the policy to use standard target names for SWIG
cmake_policy(SET CMP0078 NEW)
# Set the policy to honor SWIG_MODULE_NAME
cmake_policy(SET CMP0086 NEW)


# ============================== Load modules ============================== 
# add_subdirectory(sunlight)

# Load SWIG module
find_package(SWIG REQUIRED)
if(NOT SWIG_FOUND)
  message(FATAL_ERROR "SWIG not found!")
endif()

include(${SWIG_USE_FILE})

# Include python so swig can use it
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})


# ============================== Add sources files ============================== 
set(UseSWIG_TARGET_NAME_PREFERENCE STANDARD)

# Configuring the sunlight.i source file to be treated as C++ code by SWIG.
# It will also include STL files (string, vector...)
set_property(SOURCE pySunlight.i PROPERTY CPLUSPLUS ON)

include_directories("${CMAKE_SOURCE_DIR}/Sunlight")

# Call swig
swig_add_library(pySunlight
    LANGUAGE python
    SOURCES pySunlight.i)

target_link_libraries(pySunlight PRIVATE sunlight ${Python_LIBRARIES})