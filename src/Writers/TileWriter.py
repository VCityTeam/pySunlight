from py3dtiles import TileSet, Tile
from py3dtilers.Common import GeometryNode, FeatureList, ObjWriter, FromGeometryTreeToTileset
import copy
import numpy as np
import logging

# On the fly tile writer (write tile by tile and tileset individually)
# Avoid to store in memory the whole tileset_tree


class TileWriter():
    def __init__(self, output_directory: str = None, args=None):
        self.output_directory = output_directory
        self.args = args

    def set_output_directory(self, output_directory: str):
        """
        The function sets the output directory.

        :param output_directory: The output_directory parameter is a string that represents the
        directory where the output files will be saved
        :type output_directory: str
        """
        self.output_directory = output_directory

    def set_args(self, args):
        """
        The function sets the value of the "args" attribute of an object.

        :param args: The "args" parameter is a variable that can be used to pass in arguments to a
        method or function. It can be of any data type and can be used to provide additional information
        or values that the method or function needs to perform its task
        """
        self.args = args

    def export_tileset(self, tileset: TileSet):
        """
        The function exports a tileset by writing it as a JSON file, with each tile's content URI set to
        a specific location.

        :param tileset: The `tileset` parameter is an instance of the `TileSet` class. It represents a
        collection of tiles that make up a 3D tileset
        :type tileset: TileSet
        """
        if self.output_directory is None:
            logging.error("Output Directory is undefined. Can't export...")
            return

        # FIXME
        # Copy because changing tileset content uri will change the tile loading
        # Don't know why. It has a link with Dummy uri content set by TileContent from py3DTiles
        tileset_copy = copy.deepcopy(tileset)

        # Prior to writing the TileSet, the future location of the enclosed
        # Tile's content (set as their respective TileContent uri) must be
        # specified:
        # TODO Check with LMA if I need to create a py3DTilers issue
        all_tiles = tileset_copy.get_root_tile().get_children()
        for index, tile in enumerate(all_tiles):
            tile.set_content_uri('tiles/' + f'{index}.b3dm')

        tileset_copy.write_as_json(self.output_directory)

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile: Tile):
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
        if self.output_directory is None:
            logging.error("Output Directory is undefined. Can't export...")
            return

        # TODO Check with LMA if there is a method to recenter all features by tile centroid
        feature_list.translate_features(np.multiply(tile.get_transform()[12:15], -1))

        # TODO Check with LMA if ObjWriter and arguments are really useful
        obj_writer = ObjWriter()
        node = GeometryNode(feature_list)
        node.set_node_features_geometry(self.args)

        # Export Tile
        offset = FromGeometryTreeToTileset._FromGeometryTreeToTileset__transform_node(node, self.args, np.array([0, 0, 0]), obj_writer=obj_writer)
        FromGeometryTreeToTileset._FromGeometryTreeToTileset__create_tile(node, offset, None, self.output_directory)
