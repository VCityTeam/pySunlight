from distutils.core import setup, Extension

modules = Extension(
    "_pySunlight", sources=[
        "pySunlight_wrap.cxx",
        ]
)

setup(
    name="pySunlight",
    ext_modules=[modules],
    py_modules=["pySunlight"]
)
