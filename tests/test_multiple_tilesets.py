import unittest
from argparse import Namespace
from filecmp import cmp
from pathlib import Path

from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtiles import TilesetReader
from src.main import compute_3DTiles_sunlight
from src.pySunlight import SunDatas, Vec3d
from src.Writers import CsvWriter, TileWriter

# Test if the computed result is identical to a previous result


class TestMultipleTilesets(unittest.TestCase):
    def test_multiple_tilesets_in_csv(self):
        TESTING_DIRECTORY = 'datas/testing'

        # Define basic input
        mainTileset = TilesetReader().read_tileset(f'{TESTING_DIRECTORY}/b3dm_tileset/')
        secondTileset = TilesetReader().read_tileset(f'{TESTING_DIRECTORY}/b3dm_secondary_tileset/')
        sun_datas = SunDatas("2016-01-01:0800", Vec3d(1888857.649890, 5136065.174273, 12280.013599), Vec3d(0.748839, -0.630358, 0.204667))
        writer = CsvWriter(TESTING_DIRECTORY, 'junk.csv')
        writer.create_directory()

        # Compute result
        compute_3DTiles_sunlight(mainTileset, sun_datas, writer, secondTileset)

        # Compare CSV result
        original_file_path = str(Path(TESTING_DIRECTORY, 'original_multiple_tilesets.csv'))
        computed_file_path = str(writer.get_path())

        self.assertTrue(cmp(original_file_path, computed_file_path), 'Computation differs from the origin')

    def test_multiple_tilesets_in_tiles(self):
        TESTING_DIRECTORY = 'datas/testing'
        ORIGINAL_DIRECTORY = Path(TESTING_DIRECTORY, "b3dm_multiple_tileset")
        JUNK_DIRECTORY = Path(TESTING_DIRECTORY, 'junk_computation')

        # Define basic input
        sun_datas = SunDatas("2016-10-01:0700", Vec3d(1901882.337616, 5166061.119860, 13415.421495), Vec3d(0.965917, -0.130426, 0.223590))

        # Define tiler for TileWriter definition
        tiler = TilesetTiler()
        tiler.args = Namespace(obj=None, loa=None, lod1=False, crs_in='EPSG:3946', crs_out='EPSG:3946', offset=[0, 0, 0], with_texture=False, scale=1, output_dir=JUNK_DIRECTORY, geometric_error=[None, None, None], kd_tree_max=None, texture_lods=0)
        mainTileset = TilesetReader().read_tileset(f'{ORIGINAL_DIRECTORY}/original/')
        secondTileset = TilesetReader().read_tileset(f'{TESTING_DIRECTORY}/b3dm_secondary_tileset/')

        writer = TileWriter(JUNK_DIRECTORY, tiler)
        writer.create_directory()

        # Compute result
        compute_3DTiles_sunlight(mainTileset, sun_datas, writer, secondTileset)

        # Compare result
        for tile in mainTileset.get_root_tile().get_children():
            tile_name = tile.get_content_uri()
            original_file_path = Path(ORIGINAL_DIRECTORY, "precomputed_multiple_tilesets", tile_name)
            computed_file_path = Path(JUNK_DIRECTORY, tile_name)

            self.assertTrue(cmp(original_file_path, computed_file_path), f"Computation of tile {tile.get_content_uri()} differs from the origin")
