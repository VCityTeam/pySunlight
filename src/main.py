from py3dtilers.TilesetReader.tile_to_feature import TileToFeatureList
from pathlib import Path
import pySunlight
import numpy as np
import logging
import copy
from typing import List
from py3dtiles import TileSet, Tile
from py3dtilers.TilesetReader.TilesetReader import TilesetTiler, TilesetReader
from py3dtilers.Common import GeometryNode, FeatureList, ObjWriter
from py3dtilers.Common import FromGeometryTreeToTileset
from Converters import TilerToSunlight, SunlightToTiler
from SunlightResult import SunlightResult
import Utils


def export_tileset(tileset: TileSet, output_directory: str):
    """
    The function `export_tileset` exports a given `TileSet` object to a specified output directory, by
    modifying the content URIs of the tiles and writing the modified `TileSet` as a JSON file.

    :param tileset: The `tileset` parameter is an instance of the `TileSet` class. It represents a 3D
    tileset, which is a collection of tiles that can be used to render a 3D scene
    :type tileset: TileSet
    :param output_directory: The `output_directory` parameter is a string that specifies the directory
    where the exported tileset will be saved
    :type output_directory: str
    """
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

    tileset_copy.write_as_json(output_directory)


def export_feature_list_by_tile(feature_list: FeatureList, tile: Tile, output_directory: str, args=None):
    """
    The function exports a feature list by tile to an output directory using an ObjWriter and arguments.

    :param feature_list: A FeatureList object that contains a list of features
    :type feature_list: FeatureList
    :param tile: The "tile" parameter is an instance of the "Tile" class. It represents a specific tile
    or region in a larger dataset or map. It likely contains information such as the tile's coordinates,
    size, and transformation matrix
    :type tile: Tile
    :param output_directory: The `output_directory` parameter is a string that specifies the directory
    where the exported tile will be saved
    :type output_directory: str
    :param args: The "args" parameter is an optional argument that can be passed to the function. It is
    used to provide additional configuration or settings for the function
    """
    # TODO Check with LMA if there is a method to recenter all features by tile centroid
    feature_list.translate_features(np.multiply(tile.get_transform()[12:15], -1))

    # TODO Check with LMA if ObjWriter and arguments are really useful
    obj_writer = ObjWriter()
    node = GeometryNode(feature_list)
    node.set_node_features_geometry(args)

    # Export Tile
    offset = FromGeometryTreeToTileset._FromGeometryTreeToTileset__transform_node(node, args, np.array([0, 0, 0]), obj_writer=obj_writer)
    FromGeometryTreeToTileset._FromGeometryTreeToTileset__create_tile(node, offset, None, output_directory)


def compute_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList, tileset: TileSet, output_directory: str, args=None):
    """
    The function `compute_3DTiles_sunlight` computes sunlight on 3D tiles for multiple timestamps and
    exports the results.

    :param sun_datas_list: The `sun_datas_list` parameter is a list of `SunDatas` objects. Each
    `SunDatas` object represents sunlight data for a specific timestamp. It contains information such as
    the date and direction of the sun
    :type sun_datas_list: pySunlight.SunDatasList
    :param tileset: The `tileset` parameter is an object of the `TileSet` class. It represents a
    collection of tiles that form a 3D model or scene. The `TileSet` class likely has methods and
    properties to access and manipulate the tiles within the set
    :type tileset: TileSet
    :param output_directory: The `output_directory` parameter is a string that specifies the directory
    where the computed results will be saved
    :type output_directory: str
    :param args: The `args` parameter is an optional argument that can be passed to the
    `compute_3DTiles_sunlight` function. It is not used within the function itself, so its purpose and
    expected value would depend on how the function is being used in the broader context of your code
    """
    for i, sun_datas in enumerate(sun_datas_list):
        logging.info(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps - {sun_datas.dateStr}.")

        CURRENT_OUTPUT_DIRECTORY = Utils.get_output_directory_for_timestamp(output_directory, sun_datas.dateStr)

        # Reset the counter, because it could be incremented with the previous timestamp loop
        FromGeometryTreeToTileset.tile_index = 0

        # Loop in tileset.json
        all_tiles = tileset.get_root_tile().get_children()
        for j, tile in enumerate(all_tiles):
            result = []

            logging.debug(f"Load triangles from tile {j} ...")
            triangles = TilerToSunlight.get_triangle_soup_from_tile(tile, j)
            logging.info(f"Successfully load {len(triangles)} triangles !")

            Utils.log_memory_size_in_megabyte(triangles)

            for triangle in triangles:
                # Don't compute intersection if the triangle is already looking at the ground
                if not pySunlight.isFacingTheSun(triangle, sun_datas.direction):
                    # Associate shadow with the same triangle, because there's
                    # nothing blocking it but itself
                    result.append(SunlightResult(sun_datas.dateStr, False, triangle, triangle.getId()))
                    continue

                ray = pySunlight.constructRay(triangle, sun_datas.direction)

                # TODO Add bounding box check to avoid tile parsing / intersection checking
                # Compare current triangle with all tiles
                nearest_ray_hit = None
                for k, other_tile in enumerate(all_tiles):

                    # "Pool geometry" - Load triangles only when it's a new tile
                    if k == j:
                        other_triangles = triangles
                    else:
                        other_triangles = TilerToSunlight.get_triangle_soup_from_tile(other_tile, k)

                    # Sort result by impact distance (from near to far)
                    triangle_ray_hits = pySunlight.checkIntersectionWith(ray, other_triangles)
                    if len(triangle_ray_hits) <= 0:
                        continue

                    # Discover a closer triangle / rayHit with another bounding box
                    if not nearest_ray_hit or triangle_ray_hits[0].distance < nearest_ray_hit.distance:
                        # We consider the first triangle to be blocking
                        nearest_ray_hit = triangle_ray_hits[0]

                if nearest_ray_hit is not None:
                    nearest_hit_triangle = nearest_ray_hit.triangle
                    result.append(SunlightResult(sun_datas.dateStr, False, triangle, nearest_hit_triangle.getId()))

                # Triangle is in plain sunlight
                else:
                    result.append(SunlightResult(sun_datas.dateStr, True, triangle, ""))

            logging.info("Exporting result...")
            feature_list = SunlightToTiler.convert_to_feature_list_with_triangle_level(result)
            export_feature_list_by_tile(feature_list, tile, CURRENT_OUTPUT_DIRECTORY, args)
            logging.info("Export finished.")

        # Export tileset.json for each timestamp
        export_tileset(tileset, CURRENT_OUTPUT_DIRECTORY)
        logging.info("End computation.\n")


def add_sunlight_aggregate(sun_datas_list: pySunlight.SunDatasList, tileset: TileSet, output_directory: str, args=None):
    tileset_reader = TilesetReader()
    num_of_tiles = len(tileset.get_root_tile().get_children())

    # We group all dates to compute aggreate on different group
    dates_by_month_and_days = Utils.group_dates_by_month_and_days(sun_datas_list)

    # We compute exposure on each tile
    exposurePercentageByFeature = dict()
    for tile_index in range(0, num_of_tiles):

        # Monthly exposure computation
        num_hours_by_month = 0
        for months in dates_by_month_and_days:

            # Daily exposure computation
            for day in months:
                CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(output_directory, day)

                # Extract feature list from the current 3DTiles Sunlight
                tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
                tile = tileset.get_root_tile().get_children()[tile_index]
                feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

                for feature in feature_list:
                    id = feature.batchtable_data['id']
                    exposure = (int)(feature.batchtable_data['bLighted'])

                    # Initialize exposure percentages
                    if id not in exposurePercentageByFeature.keys():
                        exposurePercentageByFeature[id] = 0

                    exposurePercentageByFeature[id] += exposure

            # Export daily result after looping on each hour
            for day in months:
                FromGeometryTreeToTileset.tile_index = tile_index

                CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(output_directory, day)
                tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
                tile = tileset.get_root_tile().get_children()[tile_index]
                feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

                # Add daily exposure
                for feature in feature_list:
                    current_exposure = exposurePercentageByFeature[feature.batchtable_data['id']] * 100 / len(months)
                    feature.add_batchtable_data('dailyExposurePercent', current_exposure)

                export_feature_list_by_tile(feature_list, tile, CURRENT_DIRECTORY, args)

            num_hours_by_month += len(months)


def produce_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList, tileset: TileSet, output_directory: str, args=None):
    """
    The function `produce_3DTiles_sunlight` generates 3D tiles with sunlight data and adds sunlight
    aggregation.

    :param sun_datas_list: A list of sun data objects. Each sun data object contains information about
    the position and intensity of the sun at a specific time
    :type sun_datas_list: pySunlight.SunDatasList
    :param tileset: The `tileset` parameter is an object of type `TileSet`. It represents a collection
    of 3D tiles that can be rendered in a 3D viewer
    :type tileset: TileSet
    :param output_directory: The output directory is the location where the generated 3D tiles with
    sunlight information will be saved
    :type output_directory: str
    :param args: The "args" parameter is an optional argument that can be passed to the function. It can
    be used to provide additional configuration or settings for the function
    """
    compute_3DTiles_sunlight(sun_datas_list, tileset, output_directory, args)
    add_sunlight_aggregate(sun_datas_list, tileset, output_directory, args)


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

    # 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
    # 403248 corresponds to 2016-01-01 at 24:00 in 3DUSE.
    sunParser = pySunlight.SunEarthToolsParser()
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403248)

    # Read all tiles in a folder using command line arguments
    tiler = TilesetTiler()
    tiler.parse_command_line()

    # Merge all tiles to create one TileSet
    tileset = tiler.read_and_merge_tilesets()

    produce_3DTiles_sunlight(sunParser.getSunDatas(), tileset, tiler.get_output_dir(), tiler.args)


if __name__ == '__main__':
    main()
