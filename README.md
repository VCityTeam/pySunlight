# pySunlight
## Table of Contents
<ol>
  <li>
    <a href="#about-the-project">About The Project</a>
  </li>
  <li>
    <a href="#getting-started">Getting Started</a>
    <ul>
      <li><a href="#prerequisites">Prerequisites</a></li>
      <li><a href="#installation">Installation</a></li>
    </ul>
  </li>
  <li><a href="#usage">Usage</a></li>
  <li><a href="#contributing">Contributing</a>
    <ul>
      <li><a href="#coding-style">Coding Style</a></li>
      <li><a href="#pipeline---activity-chart">Pipeline</a></li>
      <li><a href="#directory-hierarchy">Directory Hierarchy</a></li>
    </ul>
  </li>
  <li><a href="#contact">Contact</a></li>
  <li><a href="#acknowledgments">Acknowledgments</a></li>
</ol>

## About The Project
Light pre-calculation based on real data (urban data and sun position) with 3DTiles. pySunlight wrap the [Sunlight project](https://github.com/VCityTeam/Sunlight/tree/master) using 
[SWIG](https://www.swig.org/) for its calculations to get the performance of c++ in python. Sunlight is present in a git submodule to ensure correct versions between the two projects.

## Getting Started
### Prerequisites
- Python 3.9, only version supported by our dependency with [py3DTilers](https://github.com/VCityTeam/py3dtilers) (a 3DTiles parsers).
- PostgreSQL / PostGIS, as it's required by py3DTilers even if pySunlight doesn't use any database functionality.
- Same CMake version as [Sunlight](https://github.com/VCityTeam/Sunlight/blob/master/README.md) 3.27.
- [SWIG 4.0](https://www.swig.org/).

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


### Installation
#### For Linux
1. Clone the repository.
   ```
   git clone --recursive https://github.com/VCityTeam/pySunlight.git && cd pySunlight/
   ```

2. Create your virtual environment.
   ```
   python3.9 -m venv venv
   ```

3. Enable your virtual environment.
   ```
   . venv/bin/activate
   ```

4. Install all prerequisites.
   ```
   pip install -e .
   ```

#### For Windows
1. Clone the repository.
   ```
   git clone --recursive https://github.com/VCityTeam/pySunlight.git && cd pySunlight/
   ```

2. Create your virtual environment.
   ```
   python3.9 -m venv venv
   ```

3. Enable your virtual environment.
   ```
   . venv/Scripts/activate
   ```

4. Install all prerequisites.
   ```
   pip install -e .
   ```

### Usage
1. You can create 3DTiles Sunlight using [Tileset Reader arguments](https://github.com/VCityTeam/py3dtilers/tree/master/py3dtilers/TilesetReader#tileset-reader), here is an example :
   ```
   python3.9 src/main.py -i "<INPUT_3DTILES_PATH>"
   ```

   It will be exported as OBJ in `datas/export/` directory.

## Contributing
### Coding Style
1. Install the additional dev requirements.
   ```bash
   pip install -e .[dev]
   ```

2. To check if the code follows the coding style, run `flake8`
   ```bash
   flake8 .
   ```

3. Configure your IDE with [autopep8 formatting extension](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8).
In VS Code, [follow this tutorial](https://www.digitalocean.com/community/tutorials/how-to-format-code-with-prettier-in-visual-studio-code)
by replacing prettier with [autopep8](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8).

### Pipeline - Activity Chart
Here is the pipeline we follow for pySunlight :
![Pipeline Activity Chart](./docs/Pipeline_Activity_Chart.png)

### Directory Hierarchy
```
pySunlight (repo)
├── Sunlight                  # Sunlight repository as git submodule
├── datas                     # Datas use for testing
├── docs                      # Documentations (original charts...)
├── src                       # Source code
├── .flake8                   # Flake8 Configuration
├── .gitignore                # Files/folders ignored by Git
├── .gitmodules               # Sunlight module commit version
├── CMakeLists.txt            # CMake file to create a crossplatform software
├── README.md
├── pySunlight.i              # SWIG interface file to expose Sunlight in python
├── setup.py                  # Install python requirements
```

## Contact
- Wesley Petit - [Website](https://wesleypetit.fr/) - wesley.petit.lemoine@gmail.com


## Acknowledgments
- [Sunlight](https://github.com/VCityTeam/Sunlight)
- [py3DTilers](https://github.com/VCityTeam/py3dtilers/tree/master)
