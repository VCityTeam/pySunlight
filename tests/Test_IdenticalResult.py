import unittest
from filecmp import cmp
from pathlib import Path

from py3dtiles import TilesetReader

from src.Writers.CsvWriter import CsvWriter
from src.main import compute_3DTiles_sunlight
from src.pySunlight import SunDatas, Vec3d


# Test if the computed result is identical to a previous result
class TestIdenticalResult(unittest.TestCase):
    def test_identical_result_in_csv(self):
        TESTING_DIRECTORY = 'datas/testing'

        # Define basic input
        tileset = TilesetReader().read_tileset(f'{TESTING_DIRECTORY}/b3dm_tileset/')
        sun_datas = SunDatas("2016-01-01:0800", Vec3d(1888857.649890, 5136065.174273, 12280.013599), Vec3d(0.748839, -0.630358, 0.204667))
        writer = CsvWriter(TESTING_DIRECTORY, 'junk.csv')
        writer.create_directory()

        # Compute result
        compute_3DTiles_sunlight(tileset, sun_datas, writer)

        # Compare CSV result
        original_file_path = str(Path(TESTING_DIRECTORY, 'original.csv'))
        computed_file_path = str(writer.get_path())

        self.assertTrue(cmp(original_file_path, computed_file_path), 'Computation differs from the origin')
