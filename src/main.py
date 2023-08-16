from typing import List
from pathlib import Path
import pySunlight
import numpy as np
import logging
import copy
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
            logging.debug(f"Successfully load {len(triangles)} triangles !")

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


def export_aggregate_for_an_entire_day(batch_key: str, aggregate: List[int], day: List[str], tile_index: int, output_directory: str, args=None):
    """
    The function add aggregate data in a tile for an entire day in batch table with a batch key.

    :param batch_key: The `batch_key` parameter is a string that represents the key used to identify the
    batch table data for each feature in the tileset
    :type batch_key: str
    :param aggregate: The `aggregate` parameter is a list of integers representing the aggregate values
    for each feature. Each integer in the list corresponds to a feature in the `feature_list` parameter
    :type aggregate: List[int]
    :param day: The `day` parameter is a list of strings representing the hours in a day. Each string
    represents an hour in the format "YY-MM-DD:HHMM"
    :type day: List[str]
    :param tile_index: The `tile_index` parameter represents the index of the tile within the tileset.
    It is used to retrieve the specific tile from the tileset for further processing
    :type tile_index: int
    :param output_directory: The `output_directory` parameter is a string that represents the directory
    where the output files will be saved. It is the path to the directory where the tileset files will
    be written
    :type output_directory: str
    :param args: The `args` parameter is an optional argument that can be passed to the function. It is
    not specified in the function signature, but it can be used to provide additional configuration or
    options to the function. The specific purpose and structure of the `args` parameter would depend on
    the context and requirements of
    """
    tileset_reader = TilesetReader()

    for hour in day:
        # Reset tile index, because it increase at each export
        FromGeometryTreeToTileset.tile_index = tile_index

        # Load tile corresponding to a given hour
        CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(output_directory, hour)
        tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
        tile = tileset.get_root_tile().get_children()[tile_index]
        feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

        # Set aggregate value
        for i, feature in enumerate(feature_list):
            current_exposure = aggregate[i]
            feature.add_batchtable_data(batch_key, current_exposure)

        export_feature_list_by_tile(feature_list, tile, CURRENT_DIRECTORY, args)


def add_sunlight_aggregate(sun_datas_list: pySunlight.SunDatasList, num_of_tiles: int, dates_by_month_and_days: List[List[str]], output_directory: str, args=None):
    """
    The `add_sunlight_aggregate` function computes the aggregate exposure of sunlight on each tile based
    on a list of sun data, and exports the results for each day and month.

    :param sun_datas_list: A list of sun data objects. Each sun data object represents the sunlight data
    for a specific timestamp
    :type sun_datas_list: pySunlight.SunDatasList
    :param num_of_tiles: The parameter `num_of_tiles` represents the total number of tiles that need to
    be processed. It is used in a loop to iterate over each tile and compute the aggregate exposure
    :type num_of_tiles: int
    :param output_directory: The `output_directory` parameter is a string that specifies the directory
    where the output files will be saved
    :type output_directory: str
    :param args: The `args` parameter is an optional argument that can be passed to the
    `add_sunlight_aggregate` function. It is not used within the function itself, so its purpose and
    expected value are not clear from the provided code. It is likely that `args` is intended to be used
    for
    """
    tileset_reader = TilesetReader()

    # We compute exposure on each tile
    for tile_index in range(0, num_of_tiles):
        logging.info(f"Compute aggregate of tile : {Utils.compute_percent(tile_index, num_of_tiles)}%...")

        # Monthly exposure computation
        monthlyExposureByFeature = []
        for i, months in enumerate(dates_by_month_and_days):
            logging.info(f"Loop in month {i + 1} on {len(dates_by_month_and_days)}")

            num_hours_by_month = 0

            # Daily exposure computation
            for j, day in enumerate(months):
                num_hours_by_day = len(day)
                num_hours_by_month += num_hours_by_day
                dailyExposureByFeature = []

                for hour in day:
                    CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(output_directory, hour)

                    # Extract feature list from the current 3DTiles Sunlight
                    tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
                    tile = tileset.get_root_tile().get_children()[tile_index]
                    feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

                    for feature_index, feature in enumerate(feature_list):
                        # Initialize exposure percentages with only one allocation
                        if len(dailyExposureByFeature) == 0:
                            dailyExposureByFeature = np.zeros(len(feature_list))

                        exposure = (int)(feature.batchtable_data['bLighted'])
                        dailyExposureByFeature[feature_index] += exposure

                # Export daily result after looping on each hour
                logging.debug(f"Exporting daily exposure percent {Utils.compute_percent(j, len(months))}% ...")

                # Convert all value in percent
                dailyExposurePercent = np.multiply(dailyExposureByFeature, 100 / num_hours_by_day)
                export_aggregate_for_an_entire_day('dailyExposurePercent', dailyExposurePercent, day, tile_index, output_directory, args)
                del dailyExposurePercent

                for hour in day:
                    FromGeometryTreeToTileset.tile_index = tile_index

                    CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(output_directory, hour)
                    tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
                    tile = tileset.get_root_tile().get_children()[tile_index]
                    feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

                    # Add daily exposure
                    for feature_index, feature in enumerate(feature_list):
                        current_exposure = dailyExposureByFeature[feature_index] * 100 / num_hours_by_day
                        feature.add_batchtable_data('dailyExposurePercent', current_exposure)

                    export_feature_list_by_tile(feature_list, tile, CURRENT_DIRECTORY, args)

                logging.debug(f"Exporting daily exposure percent completed.")

                # Sum all exposure by day
                if 0 < len(monthlyExposureByFeature):
                    monthlyExposureByFeature = np.add(dailyExposureByFeature, monthlyExposureByFeature)
                else:
                    monthlyExposureByFeature = dailyExposureByFeature

            # Export monthly result after looping on each day
            logging.debug(f"Exporting monthly exposure percent...")

            # Convert all value in percent
            monthlyExposureByFeature = np.multiply(monthlyExposureByFeature, 100 / num_hours_by_month)
            for day in months:
                export_aggregate_for_an_entire_day('monthlyExposurePercent', monthlyExposureByFeature, day, tile_index, output_directory, args)

            logging.debug(f"Exporting monthly exposure percent completed.")

        logging.info("End computation.")


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

    # We group all dates to compute aggreate on different group (by day and by month)
    dates = SunlightToTiler.get_dates_from_sun_datas_list(sun_datas_list)
    dates_by_month_and_days = Utils.group_dates_by_month_and_days(dates)

    num_of_tiles = len(tileset.get_root_tile().get_children())
    add_sunlight_aggregate(sun_datas_list, num_of_tiles, dates_by_month_and_days, output_directory, args)


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

    # 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
    # 403248 corresponds to 2016-01-01 at 24:00 in 3DUSE.
    sunParser = pySunlight.SunEarthToolsParser()
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403944)
    # sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 404664)

    # Read all tiles in a folder using command line arguments
    tiler = TilesetTiler()
    tiler.parse_command_line()

    # Merge all tiles to create one TileSet
    tileset = tiler.read_and_merge_tilesets()

    produce_3DTiles_sunlight(sunParser.getSunDatas(), tileset, tiler.get_output_dir(), tiler.args)


if __name__ == '__main__':
    main()
