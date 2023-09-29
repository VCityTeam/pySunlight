from pathlib import Path

import numpy as np
from py3dtilers.Common import (FeatureList, FromGeometryTreeToTileset,
                               GeometryNode)
from py3dtilers.TilesetReader.TilesetReader import TilesetReader, TilesetTiler
from py3dtiles import TileSet
from py3dtilers.TilesetReader.tile_to_feature import TileToFeatureList

from ..Utils import sort_batchtable_data_by_custom_order
from .Writer import Writer

# On the fly tile writer (write tile by tile and tileset individually)
# Avoid to store in memory the whole tileset_tree


class TileWriter(Writer):
    def __init__(self, directory, tiler=TilesetTiler):
        super().__init__(directory)

        self.args = tiler.args
        self.tileset_reader = TilesetReader()

    def set_args(self, args):
        """
        The function sets the value of the "args" attribute of an object.

        :param args: The "args" parameter is a variable that can be used to pass in arguments to a
        method or function. It can be of any data type and can be used to provide additional information
        or values that the method or function needs to perform its task
        """
        self.args = args

    def can_export_geometry(self):
        return True

    def export_tileset(self, tileset: TileSet):
        """
        The function exports a tileset by writing it as a JSON file, with each tile's content URI set to
        a specific location.

        :param tileset: The `tileset` parameter is an instance of the `TileSet` class. It represents a
        collection of tiles that make up a 3D tileset
        :type tileset: TileSet
        """
        super().export_tileset(tileset)

        tileset.write_as_json(self.directory)

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile_index: int):
        """
        The function exports a feature list by tile, sorting the batch table data and creating a tile
        from the geometry tree.

        :param feature_list: The `feature_list` parameter is an instance of the `FeatureList` class. It
        represents a list of features that need to be exported
        :type feature_list: FeatureList
        :param tile_index: The `tile_index` parameter is an integer that represents the index of the
        tile. It is used to identify a specific tile within a tileset
        :type tile_index: int
        """
        super().export_feature_list_by_tile(feature_list, tile_index)

        sort_batchtable_data_by_custom_order(feature_list)

        node = GeometryNode(feature_list)
        node.set_node_features_geometry(self.args)

        # Export Tile
        FromGeometryTreeToTileset.tile_index = tile_index
        offset = FromGeometryTreeToTileset._FromGeometryTreeToTileset__transform_node(node, self.args, np.array([0, 0, 0]))  # type: ignore
        FromGeometryTreeToTileset._FromGeometryTreeToTileset__create_tile(node, offset, None, self.directory)  # type: ignore

    def get_feature_list_from_tile(self, tile_index: int, root_directory: str):
        """
        The function `get_feature_list_from_tile` takes a tile index and a root directory as
        input, reads the corresponding tile from the tileset in the root directory, and returns a
        feature list extracted from the tile.

        :param tile_index: The `tile_index` parameter is an integer that represents the index of the
        tile you want to retrieve from the tileset
        :type tile_index: int
        :param root_directory: The `root_directory` parameter is a string that represents the root
        directory where the tileset is located
        :type root_directory: str
        :return: the feature list obtained from a specific tile in a tileset.
        """
        super().get_feature_list_from_tile(tile_index, root_directory)

        # Read tile corresponding to a given path
        tileset = self.tileset_reader.read_tileset(Path(root_directory))
        tile = tileset.get_root_tile().get_children()[tile_index]

        return TileToFeatureList(tile)
