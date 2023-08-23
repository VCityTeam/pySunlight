import numpy as np
from pathlib import Path

from py3dtilers.TilesetReader.tile_to_feature import TileToFeatureList
from py3dtilers.TilesetReader.TilesetReader import TilesetReader
from py3dtiles.tile import Tile

import pySunlight
import Utils
from Converters import TilerToSunlight

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


def convert_to_bounding_box(bounding_box, parent_transform, id=None, tile_name=None):
    """
    The function converts a bounding box object into an AABB (Axis-Aligned Bounding Box) object using
    the minimum and maximum coordinates of the bounding box.

    :param bounding_box: The `bounding_box` parameter is an object that represents a bounding box. It
    likely has a method called `get_corners()` that returns the corners of the bounding box as a numpy
    array
    :param id: The `id` parameter is an optional identifier for the bounding box. It can be used to
    uniquely identify the bounding box object
    :param tile_name: The `tile_name` parameter is a string that represents the name of the tile. It is
    an optional parameter and can be set to `None` if not needed
    :return: an instance of the pySunlight.AABB class, which represents an axis-aligned bounding box.
    """
    bounding_box.translate(np.multiply(parent_transform[12:15], 1))
    min = np.amin(bounding_box.get_corners(), axis=0)
    max = np.amax(bounding_box.get_corners(), axis=0)

    min_sunlight = convert_numpy_to_vec3(min)
    max_sunlight = convert_numpy_to_vec3(max)

    print(min_sunlight)

    return pySunlight.AABB(min_sunlight, max_sunlight, id, tile_name)


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


def get_triangle_soup_from_tile(tile: Tile, tileIndex: int):
    """
    The function `get_triangle_soup_from_tileset` reads and merges tiles from a folder, transforms
    buildings into triangle soup, and returns the triangle soup along with the tile name.
    :return: a triangle soup compatible with Sunlight
    """
    feature_list = get_feature_list_from_tile(tile)

    all_triangles = pySunlight.TriangleSoup()
    for feature in feature_list:

        # Convert py3DTiler triangles to sunlight triangle
        for i, triangle in enumerate(feature.get_geom_as_triangles()):
            # FIXME do not based on tile index, but more on tile.get_content_uri()
            # Content uri is a dummy value at this stade and can't be changed because it changes the result (check why)
            triangle_id = generate_triangle_id(f"tiles/{tileIndex}.b3dm", feature.get_id(), i)

            sunlight_triangle = convert_to_sunlight_triangle(triangle, triangle_id, tile.get_content_uri())

            all_triangles.push_back(sunlight_triangle)

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
