from distutils.core import setup, Extension

modules = Extension(
    "_sunlight", sources=[
        "sunlight_wrap.cxx",
        ]
)

setup(
    name="sunlight",
    ext_modules=[modules],
    py_modules=["sunlight"]
)
