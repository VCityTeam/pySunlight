from py3dtiles.tile import Tile

from src.Converters import TilerToSunlight
from src.pySunlight import BoundingBoxes

# The TileWrapper class is a wrapper class for tiles containing Sunlight supported types
# (TriangleSoup, AABB...)


class TileWrapper():
    def __init__(self, tile: Tile, tile_index: int):
        """
        The function initializes a wrapper by creating a triangle soup supported by Sunlight from a tile and its index, and
        converting the tile's bounding box to a Sunlight bounding box.

        :param tile: The `tile` parameter is an object of the `Tile` class. It represents a tile in a
        tiling system
        :type tile: Tile
        :param tile_index: The `tile_index` parameter is an integer that represents the index of a tile.
        It is used to identify a specific tile within a collection or set of tiles
        :type tile_index: int
        """
        self.triangle_soup = TilerToSunlight.get_triangle_soup_from_tile(tile, tile_index)
        self.index = tile_index

        # Read bounding box in tile content and convert to Sunlight bounding box (AABB)
        bounding_box = TilerToSunlight.convert_to_bounding_box(tile.get_bounding_volume(), tile.get_transform(), str(tile_index), tile.get_content_uri())

        # Contain only one bounding box, because Sunlight API require a list of bounding box
        self.bounding_box = BoundingBoxes()
        self.bounding_box.push_back(bounding_box)

    def get_tile_index(self):
        """
        The function returns the index of a tile.
        :return: the value of the variable "self.index".
        """
        return self.index

    def get_bounding_box(self):
        """
        The function returns the Sunlight bounding box of a tile.
        :return: The bounding box of the object.
        """
        return self.bounding_box

    def get_triangles(self):
        """
        The function returns the converted geometies in Sunlight.TriangleSoup.
        :return: Sunlight.TriangleSoup - The method is returning the variable "self.triangle_soup".
        """
        return self.triangle_soup
