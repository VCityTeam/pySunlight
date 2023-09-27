import numpy as np
from ..Utils import sort_batchtable_data_by_custom_order
from py3dtilers.Common import (FeatureList, FromGeometryTreeToTileset, GeometryNode)
from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtiles import Tile, TileSet

from .Writer import Writer

# On the fly tile writer (write tile by tile and tileset individually)
# Avoid to store in memory the whole tileset_tree


class TileWriter(Writer):
    def __init__(self, directory, tiler=TilesetTiler):
        super().__init__(directory)

        self.args = tiler.args

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

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile: Tile, tile_index: int):
        """
        The function exports a feature list by translating its features, creating a geometry node, and
        then exporting it as a tile.

        :param feature_list: The `feature_list` parameter is an object of type `FeatureList`. It
        represents a list of features that you want to export
        :type feature_list: FeatureList
        :param tile: The "tile" parameter is an instance of the "Tile" class. It is used to specify a
        specific tile for exporting a feature list
        :type tile: Tile
        """
        super().export_feature_list_by_tile(feature_list, tile, tile_index)

        # TODO Check with LMA if there is a method to recenter all features by tile centroid
        feature_list.translate_features(np.multiply(tile.get_transform()[12:15], -1))

        sort_batchtable_data_by_custom_order(feature_list)

        node = GeometryNode(feature_list)
        node.set_node_features_geometry(self.args)

        # Export Tile
        FromGeometryTreeToTileset.tile_index = tile_index
        offset = FromGeometryTreeToTileset._FromGeometryTreeToTileset__transform_node(node, self.args, np.array([0, 0, 0]))  # type: ignore
        FromGeometryTreeToTileset._FromGeometryTreeToTileset__create_tile(node, offset, None, self.directory)  # type: ignore
