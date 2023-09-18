import copy
import logging
from pathlib import Path

import numpy as np
from py3dtilers.Common import FeatureList, Feature
from py3dtilers.TilesetReader.tile_to_feature import TileToFeatureList
from py3dtilers.TilesetReader.TilesetReader import TilesetReader
from py3dtiles import TileSet
from py3dtiles.bounding_volume_box import BoundingVolumeBox
from py3dtiles.tile import Tile

from .. import pySunlight, Utils
from ..Converters import TilerToSunlight

# This file convert py3DTiler type to Sunlight type


def convert_numpy_to_vec3(coordinate_array):
    """
    Convert numpy array of size 3 to a Vec3D for sunlight usage
    :param coordinate_array: array of coordinate (x, y and z) coming from numpy
    :return: the conversion in Vec3D of a given coordinate array
    """
    return pySunlight.Vec3d(coordinate_array[0], coordinate_array[1], coordinate_array[2])


def convert_to_sunlight_triangle(tiler_triangle, triangle_id=None, tile_name=None):
    """
    The function converts a tiler triangle into a sunlight triangle by converting the numpy arrays to
    vec3 objects and creating a Triangle object with the given triangle ID and tile name.

    :param tiler_triangle: The `tiler_triangle` parameter is a numpy array representing a triangle in a
    tiler system. It contains three vertices of the triangle
    :param triangle_id: The `triangle_id` parameter is used to identify the triangle. It can be any
    value that uniquely identifies the triangle
    :return: a Triangle object.
    """
    a = convert_numpy_to_vec3(tiler_triangle[0])
    b = convert_numpy_to_vec3(tiler_triangle[1])
    c = convert_numpy_to_vec3(tiler_triangle[2])

    return pySunlight.Triangle(a, b, c, triangle_id, tile_name)


def convert_to_bounding_box(bounding_box: BoundingVolumeBox, parent_transform=None, id=None, tile_name=None):
    """
    The function `convert_to_bounding_box` takes a bounding box object, a parent transform, an optional
    ID, and an optional tile name, and returns a new AABB object with the minimum and maximum corners of
    the bounding box translated by the parent transform.

    :param bounding_box: The `bounding_box` parameter is an instance of the `BoundingVolumeBox` class,
    which represents a 3D bounding box volume
    :type bounding_box: BoundingVolumeBox
    :param parent_transform: The parent_transform parameter is a 4x4 transformation matrix that
    represents the transformation applied to the bounding box. It is used to translate the bounding box
    in 3D space
    :param id: The `id` parameter is an optional identifier for the bounding box. It can be used to
    uniquely identify the bounding box for further processing or referencing purposes
    :param tile_name: The `tile_name` parameter is a string that represents the name of the tile. It is
    used as an identifier for the bounding box
    :return: an instance of the `pySunlight.AABB` class, which represents an axis-aligned bounding box.
    """
    # Avoid to change bounding box properties
    bounding_box_copy = copy.deepcopy(bounding_box)

    # Translate bounding box using parent transform if needed
    if parent_transform is not None:
        bounding_box_copy.translate(np.multiply(parent_transform[12:15], 1))

    min = np.amin(bounding_box_copy.get_corners(), axis=0)
    max = np.amax(bounding_box_copy.get_corners(), axis=0)

    min_sunlight = convert_numpy_to_vec3(min)
    max_sunlight = convert_numpy_to_vec3(max)

    return pySunlight.AABB(min_sunlight, max_sunlight, id, tile_name)


def get_tiles_bounding_boxes_from_tileset(tileset: TileSet):
    """
    The function `get_tiles_bounding_boxes_from_tileset` takes a `TileSet` object, retrieves all the
    tiles from it, converts their bounding volumes to bounding boxes, and returns a collection of these
    bounding boxes.

    :param tileset: The parameter "tileset" is of type TileSet
    :type tileset: TileSet
    :return: a collection of bounding boxes for each tile in the given tileset.
    """
    all_tiles = tileset.get_root_tile().get_children()

    bounding_boxes = pySunlight.BoundingBoxes()
    for i, tile in enumerate(all_tiles):
        bounding_volume = TilerToSunlight.convert_to_bounding_box(tile.get_bounding_volume(), tile.get_transform(), str(i), tile.get_content_uri())
        bounding_boxes.append(bounding_volume)

    return bounding_boxes


def get_bounding_boxes_from_feature_list(feature_list: FeatureList):
    """
    The function `get_bounding_boxes_from_feature_list` takes a list of features and converts their
    bounding volumes into sunlight bounding boxes.

    :param feature_list: The `feature_list` parameter is of type `FeatureList`. It is a list of features
    that you want to extract bounding boxes from. Each feature in the list should have a method
    `get_bounding_volume_box()` that returns the bounding volume box of the feature
    :type feature_list: FeatureList
    :return: a list of bounding boxes.
    """
    bounding_boxes = pySunlight.BoundingBoxes()

    for i, feature in enumerate(feature_list):
        # Check bounding volume integrity
        bounding_box_tiler = feature.get_bounding_volume_box()
        if bounding_box_tiler is None:
            logging.warn('Undefined bounding volume on feature {i}')
            continue

        # Convert bounding volume to sunlight bounding box
        bounding_box = TilerToSunlight.convert_to_bounding_box(bounding_box_tiler, None, str(i), "0")
        bounding_boxes.append(bounding_box)

    return bounding_boxes


def generate_triangle_id(tile_name, feature_id, triangle_index: int):
    """
    The function generates a unique identifier for a triangle within a specific tile and feature.

    :param tile_name: The name of the tile
    :param feature_id: The feature_id parameter is used to identify a specific feature within a tile
    :param triangle_index: The `triangle_index` parameter is an integer that represents the index of a
    triangle within a feature
    :type triangle_index: int
    :return: a string that represents the ID of a triangle.
    """
    return f"Tile-{tile_name}__Feature-{feature_id}__Triangle-{triangle_index}"


def get_feature_list_from_tile(tile: Tile):
    """
    The function takes a tile object, converts it to a feature list, and then translates the features by
    the tile's centroid or offset.

    :param tile: The parameter "tile" is an object of the class "Tile"
    :type tile: Tile
    :return: a feature list.
    """
    # Convert to feature list
    feature_list = TileToFeatureList(tile)
    # Add tile centroid / offset in all coordinates
    feature_list.translate_features(tile.get_transform()[12:15])

    return feature_list


def add_triangles_from_feature(triangle_soup: pySunlight.TriangleSoup, feature: Feature, tile: Tile, tile_index: int):
    """
    The function `add_triangles_from_feature` converts triangles from a feature into sunlight triangles
    and adds them to a triangle soup.

    :param triangle_soup: `triangle_soup` is an instance of the `TriangleSoup` class from the
    `pySunlight` module. It represents a collection of triangles
    :type triangle_soup: pySunlight.TriangleSoup
    :param feature: The `feature` parameter is an object that represents a geometric feature. It likely
    contains information such as the geometry (e.g., points, lines, polygons) and attributes (e.g.,
    name, color) of the feature
    :type feature: Feature
    :param tile: The `tile` parameter is an object of type `Tile`. It likely represents a tile in a 3D
    tiling system, such as the one used in the 3D Tiles specification
    :type tile: Tile
    :param tile_index: The `tile_index` parameter is an integer that represents the index of the tile.
    It is used to generate a unique triangle ID for each triangle in the feature
    :type tile_index: int
    """
    # Convert py3DTiler triangles to sunlight triangle
    for i, triangle in enumerate(feature.get_geom_as_triangles()):
        triangle_id = generate_triangle_id(tile.get_content_uri(), feature.get_id(), i)
        sunlight_triangle = convert_to_sunlight_triangle(triangle, triangle_id, tile.get_content_uri())
        triangle_soup.push_back(sunlight_triangle)


def get_triangle_soup_from_tile(tile: Tile, tile_index: int):
    """
    The function "get_triangle_soup_from_tile" takes a tile and its index, extracts features from the
    tile, creates a triangle soup, adds triangles from each feature to the soup, and returns the
    resulting triangle soup.

    :param tile: The `tile` parameter is an object of type `Tile`. It likely represents a tile or a
    section of a larger map or grid. The specific details of the `Tile` class are not provided in the
    code snippet, so it's difficult to determine the exact properties and methods of the `Tile
    :type tile: Tile
    :param tile_index: The `tile_index` parameter is an integer that represents the index of the tile.
    It is used to identify the specific tile within a larger set of tiles
    :type tile_index: int
    :return: a `TriangleSoup` object.
    """
    feature_list = get_feature_list_from_tile(tile)

    all_triangles = pySunlight.TriangleSoup()
    for feature in feature_list:
        add_triangles_from_feature(all_triangles, feature, tile, tile_index)

    return all_triangles


def get_feature_list_from_tile_index_at(tile_index: int, tileset_reader: TilesetReader, root_directory: str, hour: str):
    """
    The function `get_feature_list_from_tile_index_at` takes a tile index, a tileset reader, a root
    directory, and an hour as input, and returns a feature list extracted from the tile at the given
    index.

    :param tile_index: The index of the tile you want to retrieve the feature list from
    :type tile_index: int
    :param tileset_reader: The `tileset_reader` parameter is an object of type `TilesetReader`. It is
    responsible for reading the tileset from a given directory
    :type tileset_reader: TilesetReader
    :param root_directory: The root directory is the main directory where the tileset files are stored.
    It is the starting point for accessing the tileset data
    :type root_directory: str
    :param hour: The `hour` parameter is a string representing the hour at which the tile index is being
    retrieved
    :type hour: str
    :return: a feature list extracted from a specific tile in a tileset.
    """
    CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(root_directory, hour)
    tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
    tile = tileset.get_root_tile().get_children()[tile_index]
    return TilerToSunlight.get_feature_list_from_tile(tile)
