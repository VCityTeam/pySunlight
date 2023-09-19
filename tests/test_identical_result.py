import unittest
from argparse import Namespace
from filecmp import cmp
from pathlib import Path

from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtiles import TilesetReader
from src.main import compute_3DTiles_sunlight
from src.pySunlight import SunDatas, Vec3d
from src.Writers.CsvWriter import CsvWriter
from src.Aggregators.AggregatorController import AggregatorControllerInBatchTable
import shutil

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

    def test_identical_result_with_aggregate(self):
        # Trigger bug describe here : https://github.com/VCityTeam/pySunlight/issues/7

        # Path of exported result
        TESTING_DIRECTORY = 'datas/testing'
        ORIGINAL_DIRECTORY = Path(TESTING_DIRECTORY, "b3dm_multiple_tileset")
        JUNK_DIRECTORY = Path(TESTING_DIRECTORY, "junk_aggregate_result")

        # Copy precomputed tileset to recompute and export aggregate on it
        shutil.copytree(str(Path(ORIGINAL_DIRECTORY, "precomputed_sunlight")), str(JUNK_DIRECTORY), dirs_exist_ok=True)

        # Set 3D Tiles testing configurations
        tiler = TilesetTiler()
        tiler.args = Namespace(obj=None, loa=None, lod1=False, crs_in='EPSG:3946',
                               crs_out='EPSG:3946', offset=[0, 0, 0], with_texture=False, scale=1,
                               output_dir=JUNK_DIRECTORY, geometric_error=[None, None, None], kd_tree_max=None,
                               texture_lods=0)
        tiler.files = [ORIGINAL_DIRECTORY]

        # Compute and export aggregate
        aggregator = AggregatorControllerInBatchTable(tiler.get_output_dir(), tiler)
        aggregator.compute_and_export(num_of_tiles=2, dates_by_month_and_days=[[['2016-10-01:0700']]])

        # Compare result
        original_file_path = Path(ORIGINAL_DIRECTORY, "precomputed_aggregate/2016-10-01__0700/tiles/0.b3dm")
        computed_file_path = Path(JUNK_DIRECTORY, "2016-10-01__0700/tiles/0.b3dm")
        self.assertTrue(cmp(original_file_path, computed_file_path), 'Aggregate differs from the origin')

        original_file_path = Path(ORIGINAL_DIRECTORY, "precomputed_aggregate/2016-10-01__0700/tiles/1.b3dm")
        computed_file_path = Path(JUNK_DIRECTORY, "2016-10-01__0700/tiles/1.b3dm")
        self.assertTrue(cmp(original_file_path, computed_file_path), 'Aggregate differs from the origin')
