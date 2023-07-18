# pySunlight

## Getting Started
### Prerequisites
- Python 3.9, only version supported by our dependency with [py3DTilers](https://github.com/VCityTeam/py3dtilers) (a 3DTiles parsers).
- PostgreSQL / PostGIS, because it's required by py3DTilers even if pySunlight doesn't use any database features.
- Same CMake version as [Sunlight](https://github.com/VCityTeam/Sunlight/blob/master/README.md) 3.27.
- [Swig 4.0](https://www.swig.org/).

#### For Linux
1. Install python 3.9.
```
apt-get install python3.9 python3.9-dev
```

2. Install virtual environment library (recommanded).
```
apt-get install virtualenv git
```

3. [Follow the install guide of PostgreSQL / PostGIS](https://github.com/VCityTeam/UD-SV/blob/master/Install/Setup_PostgreSQL_PostGIS_Ubuntu.md).

4. Install [libpq](https://www.postgresql.org/docs/9.5/libpq.html), the client interface with PostgreSQL in C. (required by psycopg2 within py3dtilers).
```
apt-get install -y libpq-dev
```

5. Install swig 4.0.
```
apt-get install swig4.0
ln -s /usr/bin/swig4.0 /usr/bin/swig
```

#### For Windows
1. Download and install pyhon 3.9 from the [official website](https://www.python.org/downloads/windows/).

2. [Follow the install guide of PostgreSQL / PostGIS.](https://github.com/VCityTeam/UD-SV/blob/master/ImplementationKnowHow/PostgreSQL_for_cityGML.md#1-download-postgresqlpostgis).

4. [Download CMake 3.27](https://cmake.org/download/).

5. Download SWIG for Windows from SWIG [Download Page](https://sourceforge.net/projects/swig/files/swigwin/swigwin-4.0.2/).

6. Unzip the files after downloading.

7. Add the SWIG folder in your environments variables under SYSTEM PATH.

8. Open a terminal and check your swig version :
```
swig -version
```
If the process was successful, you will see your swig version.  
Else, you can verify in the [SWIG manual](https://github.com/swig/swig/blob/master/Doc/Manual/Windows.html) for more instructions.

### Install
#### For Linux
1. Clone the repository.
```
git clone https://github.com/VCityTeam/pySunlight.git
```

2. Go to the pySunlight directory.
```
cd pySunlight/
```

3. Create a build folder that will contain Sunlight wrapper.
```
mkdir build/
```

4. Compile pySunlight.
``` bash
cd build/
cmake .. && make
```

5. Create your virtual environment.
```
virtualenv -p python3.9 venv
```

6. Enable your virtual environment.
```
. venv/bin/activate
```

7. Install all prerequisites.
```
pip install -e .
```

#### For Windows
1. Clone the repository.
```
git clone https://github.com/VCityTeam/pySunlight.git
```

2. Create a build folder in pySunlight that will contains the build of Sunlight and SWIG.

3. Open CMake and specify the source code path (pySunlight root folder) and the build binaries path (pySunlight/build).

4. Click on Configure, Generate then Open Project.

5. In Visual Studio, build the solution on release.

6. Open a terminal and go to the pySunlight directory.
```
cd pySunlight/
```

7. Create your virtual environment.
```
python3.9 -m venv venv
```

8. Enable your virtual environment.
```
. venv/Scripts/activate
```

9. Install all prerequisites.
```
pip install -e .
```
