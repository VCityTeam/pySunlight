# CMakeLists.txt
cmake_minimum_required(VERSION 3.2)
project(pySunlight LANGUAGES CXX)

# Set the policy to use standard target names for SWIG
cmake_policy(SET CMP0078 NEW)
# Set the policy to honor SWIG_MODULE_NAME
cmake_policy(SET CMP0086 NEW)


# ============================== Load modules ============================== 
add_subdirectory(Sunlight)

# Load SWIG module
find_package(SWIG REQUIRED)
if(NOT SWIG_FOUND)
  message(FATAL_ERROR "SWIG not found!")
endif()

include(${SWIG_USE_FILE})

# Include python so swig can use it
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
if (NOT Python3_FOUND)
  message(FATAL_ERROR "Python3 not found!")
endif()

# ============================== Add sources files ============================== 
set(UseSWIG_TARGET_NAME_PREFERENCE STANDARD)

# Configuring the sunlight.i source file to be treated as C++ code by SWIG.
# It will also include STL files (string, vector...)
set_property(SOURCE pySunlight.i PROPERTY CPLUSPLUS ON)

# Add include of all sources of sunlight
include_directories(pySunlight PUBLIC "${CMAKE_SOURCE_DIR}/Sunlight/src/")

# Call swig
swig_add_library(pySunlight
    LANGUAGE python

    # Export path of the module
    OUTPUT_DIR ${CMAKE_SOURCE_DIR}
    
    # Export path of the c++ wrapper (*_wrap.cxx)
    OUTFILE_DIR "${CMAKE_SOURCE_DIR}/build"

    SOURCES pySunlight.i)

target_compile_features(pySunlight PRIVATE cxx_std_20)

target_link_libraries(pySunlight PUBLIC sunlight)

# Include Python
target_include_directories(pySunlight PRIVATE ${Python3_INCLUDE_DIRS})
# target_include_directories(pySunlight PRIVATE ${Python3_LIBRARIES})

# Move the library generated (*.so)
set_target_properties(pySunlight PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})