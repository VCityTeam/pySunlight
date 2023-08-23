import csv
from Writers import CsvWriter

# Test if the computed result is identical to a previous result

from pathlib import Path

from filecmp import cmp

from main import compute_3DTiles_sunlight

from pySunlight import SunDatas, Vec3d

from argparse import Namespace
from py3dtilers.TilesetReader.TilesetReader import TilesetTiler


from py3dtiles import TilesetReader


def main():
    TESTING_DIRECTORY = 'datas/testing'

    # Define basic input
    tileset = TilesetReader().read_tileset(f'{TESTING_DIRECTORY}/b3dm_tileset/')
    sun_datas = SunDatas("2016-01-01:0800", Vec3d(1888857.649890, 5136065.174273, 12280.013599), Vec3d(0.748839, -0.630358, 0.204667))
    writer = CsvWriter(TESTING_DIRECTORY, 'junk.csv')

    # Compute result
    compute_3DTiles_sunlight(tileset, sun_datas, writer)

    # Compare CSV result
    original_file_path = str(Path(TESTING_DIRECTORY, 'original.csv'))
    computed_file_path = str(writer.get_path())

    if cmp(original_file_path, computed_file_path):
        print("The CSV files are identical.")
    else:
        print("The CSV files are not identical.")


if __name__ == '__main__':
    main()
