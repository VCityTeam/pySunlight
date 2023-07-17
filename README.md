# pySunlight

## Getting Started
### Prerequisites
At the moment, we support only python 3.9, because of our dependency with [py3DTilers](https://github.com/VCityTeam/py3dtilers) (a 3DTiles parsers).  
You will also need PostgreSQL, because it's required by py3DTilers even if pySunlight doesn't use any database features.

#### For Linux
1. Install python 3.9.
```
apt-get install python3.9 python3.9-dev
```

2. Install virtual environment library (recommanded).
```
apt-get install virtualenv git
```

3. [Follow the install guide of PostgreSQL / PostGIS.](https://github.com/VCityTeam/UD-SV/blob/master/Install/Setup_PostgreSQL_PostGIS_Ubuntu.md).

4. Install [libpq](https://www.postgresql.org/docs/9.5/libpq.html), the client interface with PostgreSQL in C. (required by psycopg2 within py3dtilers).
```
apt-get install -y libpq-dev
```

#### For Windows
1. Download and install pyhon 3.9 from the [official website](https://www.python.org/downloads/windows/).

2. [Follow the install guide of PostgreSQL / PostGIS.](https://github.com/VCityTeam/UD-SV/blob/master/ImplementationKnowHow/PostgreSQL_for_cityGML.md#1-download-postgresqlpostgis).

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

3. Create your virtual environment.
```
virtualenv -p python3.9 venv
```

4. Enable your virtual environment.
```
. venv/bin/activate
```

5. Install all prerequisites.
```
pip install -e .
```

#### For Windows
1. Clone the repository.
```
git clone https://github.com/VCityTeam/pySunlight.git
```

2. Go to the pySunlight directory.
```
cd pySunlight/
```

3. Create your virtual environment.
```
python3.9 -m venv venv
```

4. Enable your virtual environment.
```
. venv/Scripts/activate
```

5. Install all prerequisites.
```
pip install -e .
```
