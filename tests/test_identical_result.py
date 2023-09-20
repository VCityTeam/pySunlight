import unittest
from argparse import Namespace
from filecmp import cmp
from pathlib import Path

from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtiles import TilesetReader
from src.main import compute_3DTiles_sunlight
from src.pySunlight import SunDatas, Vec3d
from src.Writers import CsvWriter, TileWriter
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

    def test_identical_result_in_tiles(self):
        TESTING_DIRECTORY = 'datas/testing'
        ORIGINAL_DIRECTORY = Path(TESTING_DIRECTORY, "b3dm_multiple_tileset")
        JUNK_DIRECTORY = Path(TESTING_DIRECTORY, 'junk_computation')

        # Define basic input
        sun_datas = SunDatas("2016-10-01:0700", Vec3d(1901882.337616, 5166061.119860, 13415.421495), Vec3d(0.965917, -0.130426, 0.223590))

        # Define tiler for TileWriter definition
        tiler = TilesetTiler()
        tiler.args = Namespace(obj=None, loa=None, lod1=False, crs_in='EPSG:3946', crs_out='EPSG:3946', offset=[0, 0, 0], with_texture=False, scale=1, output_dir=JUNK_DIRECTORY, geometric_error=[None, None, None], kd_tree_max=None, texture_lods=0)
        tileset = TilesetReader().read_tileset(f'{ORIGINAL_DIRECTORY}/original/')

        writer = TileWriter(JUNK_DIRECTORY, tiler)
        writer.create_directory()

        # Compute result
        compute_3DTiles_sunlight(tileset, sun_datas, writer)

        # Compare result
        for tile in tileset.get_root_tile().get_children():
            tile_name = tile.get_content_uri()
            original_file_path = Path(ORIGINAL_DIRECTORY, "precomputed_sunlight/2016-10-01__0700", tile_name)
            computed_file_path = Path(JUNK_DIRECTORY, tile_name)

            self.assertTrue(cmp(original_file_path, computed_file_path), f"Computation of tile {tile.get_content_uri()} differs from the origin")

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
        tiler.args = Namespace(obj=None, loa=None, lod1=False, crs_in='EPSG:3946', crs_out='EPSG:3946', offset=[0, 0, 0], with_texture=False, scale=1, output_dir=JUNK_DIRECTORY, geometric_error=[None, None, None], kd_tree_max=None, texture_lods=0)
        tiler.files = [ORIGINAL_DIRECTORY]
        tileset = tiler.read_and_merge_tilesets()

        # Compute and export aggregate
        num_of_tiles = len(tileset.get_root_tile().get_children())
        aggregator = AggregatorControllerInBatchTable(tiler.get_output_dir(), tiler)
        aggregator.compute_and_export(num_of_tiles, dates_by_month_and_days=[[['2016-10-01:0700']]])

        # Compare result
        for tile in tileset.get_root_tile().get_children():
            tile_name = f"2016-10-01__0700/{tile.get_content_uri()}"
            original_file_path = Path(ORIGINAL_DIRECTORY, "precomputed_aggregate", tile_name)
            computed_file_path = Path(JUNK_DIRECTORY, tile_name)

            self.assertTrue(cmp(original_file_path, computed_file_path), f"Aggregate of tile {tile.get_content_uri()} differs from the origin")
