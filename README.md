# pySunlight

## Getting Started
### Prerequisites
- Python 3.9, only version supported by our dependency with [py3DTilers](https://github.com/VCityTeam/py3dtilers) (a 3DTiles parsers).
- PostgreSQL / PostGIS, as it's required by py3DTilers even if pySunlight doesn't use any database functionality.
- Same CMake version as [Sunlight](https://github.com/VCityTeam/Sunlight/blob/master/README.md) 3.27.
- [Swig 4.0](https://www.swig.org/).

#### For Linux
1. Install python 3.9.
   ```
   apt-get install python3.9 python3.9-dev
   ```

2. [Follow the install guide of PostgreSQL / PostGIS](https://github.com/VCityTeam/UD-SV/blob/master/Install/Setup_PostgreSQL_PostGIS_Ubuntu.md).

3. Install [libpq](https://www.postgresql.org/docs/9.5/libpq.html), the client interface with PostgreSQL in C. (required by psycopg2 within py3dtilers).
   ```
   apt-get install -y libpq-dev
   ```

4. [Follow the SWIG install for Linux](https://github.com/VCityTeam/UD-SV/blob/master/Install/InstallSwig.md#for-linux).


#### For Mac OS
1. Download and install python 3.9 from the [official website](https://www.python.org/downloads/macos/).

2. ⚠️ FIX ME : add PostgreSQL / PostGIS Mac os ?????

3. [Follow the SWIG install for Mac Os](https://github.com/VCityTeam/UD-SV/blob/master/Install/InstallSwig.md#wor-mac-os).


#### For Windows
1. Download and install python 3.9 from the [official website](https://www.python.org/downloads/windows/).

2. [Follow the install guide of PostgreSQL / PostGIS](https://github.com/VCityTeam/UD-SV/blob/master/ImplementationKnowHow/PostgreSQL_for_cityGML.md#1-download-postgresqlpostgis).

3. [Download CMake 3.27](https://cmake.org/download/).

4. [Follow the SWIG install for Windows](https://github.com/VCityTeam/UD-SV/blob/master/Install/InstallSwig.md#for-windows).


### Install
#### For Linux
1. Clone the repository.
   ```
   git clone --recursive https://github.com/VCityTeam/pySunlight.git
   ```

2. Create a build folder that will contain Sunlight wrapper.
   ```
   cd pySunlight/ && mkdir build/
   ```

3. Compile pySunlight.
   ``` bash
   cd build/
   cmake .. && make
   ```

4. Create your virtual environment.
   ```
   python3.9 -m venv venv
   ```

5. Enable your virtual environment.
   ```
   . venv/bin/activate
   ```

6. Install all prerequisites.
   ```
   pip install -e .
   ```

#### For Windows
1. Clone the repository.
   ```
   git clone --recursive https://github.com/VCityTeam/pySunlight.git
   cd pySunlight/
   ```

2. Create a build folder in pySunlight that will contains the build of Sunlight and SWIG.

3. Open CMake and specify the source code path (pySunlight root folder) and the build binaries path (pySunlight/build).

4. Click on Configure, Generate then Open Project.

5. In Visual Studio, build the solution on release.

6. Create your virtual environment.
   ```
   python3.9 -m venv venv
   ```

7. Enable your virtual environment.
   ```
   . venv/Scripts/activate
   ```

8. Install all prerequisites.
   ```
   pip install -e .
   ```

### Usage
1. You can create 3DTiles Sunlight using [Tileset Reader arguments](https://github.com/VCityTeam/py3dtilers/tree/master/py3dtilers/TilesetReader#tileset-reader), here is an example :
   ```
   python3.9 main.py -i "<INPUT_3DTILES_PATH>" -o "<OUTPUT_3DTILES_PATH>"
   ```
