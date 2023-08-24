import argparse
import logging

from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtiles import TileSet

from src import pySunlight
from src import Utils
from src.Aggregators.AggregatorController import AggregatorControllerInBatchTable
from src.Converters import SunlightToTiler, TilerToSunlight
from src.SunlightResult import SunlightResult
from src.Writers import CsvWriter, TileWriter, Writer

import numpy as np

from typing import List


def compute_3DTiles_sunlight(tileset: TileSet, sun_datas: pySunlight.SunDatas, writer: Writer):
    """
    The function `compute_3DTiles_sunlight` computes sunlight visibility for each triangle in a 3D
    tileset and exports the results.

    :param tileset: The `tileset` parameter is an object of type `TileSet`. It represents a collection
    of tiles that make up a 3D model or scene
    :type tileset: TileSet
    :param sun_datas: The `sun_datas` parameter is an object of type `pySunlight.SunDatas`. It contains
    information about the sun, such as the date and direction
    :type sun_datas: pySunlight.SunDatas
    :param writer: The `writer` parameter is an object of the `Writer` class. It is used to export the
    computed results and the updated `tileset.json` file
    :type writer: Writer
    """
    # Construct bounding boxes by tiles
    tiles_bounding_boxes = TilerToSunlight.get_tiles_bounding_boxes_from_tileset(tileset)

    # Loop in tileset.json
    all_tiles = tileset.get_root_tile().get_children()
    for j, tile in enumerate(all_tiles):
        logging.debug(f"Load triangles from tile {j} ...")
        triangles = TilerToSunlight.get_triangle_soup_from_tile(tile, j)
        Utils.log_memory_size_in_megabyte(triangles)
        logging.debug(f"Successfully load {len(triangles)} triangles !")

        # Intialize containers
        results = [None] * len(triangles)
        # Contain ray hits accross the whole tile comparaison
        ray_hits_by_index = dict()

        # We loop on tiles to compare with triangle in order to load a tile once
        # and not for each triangle
        for other_tile_id, other_tile in enumerate(all_tiles):
            # Get all tile properties
            bounding_boxes = pySunlight.BoundingBoxes()
            bounding_boxes.append(tiles_bounding_boxes[other_tile_id])

            other_triangle_soup = TilerToSunlight.get_triangle_soup_from_tile(other_tile, other_tile_id)

            for triangle_index, triangle in enumerate(triangles):
                # Don't compute intersection if the triangle is already looking at the ground
                if not pySunlight.isFacingTheSun(triangle, sun_datas.direction):
                    # Associate shadow with the same triangle, because there's
                    # nothing blocking it but itself
                    results[triangle_index] = SunlightResult(sun_datas.dateStr, False, triangle, triangle.getId())  # type: ignore
                    continue

                ray = pySunlight.constructRay(triangle, sun_datas.direction)
                nearest_ray_hit = None

                # Compare current triangle with all tiles
                tile_bounding_boxes_hit = pySunlight.checkIntersectionWith(ray, bounding_boxes)
                if len(tile_bounding_boxes_hit) != 0:
                    # Sort result by impact distance (from near to far)
                    triangle_ray_hits = pySunlight.checkIntersectionWith(ray, other_triangle_soup)

                    # Discover a closer triangle / rayHit with another bounding box
                    if 0 < len(triangle_ray_hits) and (not nearest_ray_hit or triangle_ray_hits[0].distance < nearest_ray_hit.distance):
                        # We consider the first triangle to be blocking
                        nearest_ray_hit = triangle_ray_hits[0]

                # Record result
                if nearest_ray_hit is not None:
                    nearest_hit_triangle = nearest_ray_hit.triangle
                    ray_hits_by_index[triangle_index] = nearest_ray_hit

                    results[triangle_index] = SunlightResult(sun_datas.dateStr, False, triangle, nearest_hit_triangle.getId())  # type: ignore

                # Triangle is in plain sunlight
                else:
                    results[triangle_index] = SunlightResult(sun_datas.dateStr, True, triangle, "")  # type: ignore

        logging.info("Exporting result...")
        feature_list = SunlightToTiler.convert_to_feature_list_with_triangle_level(results)  # type: ignore
        writer.export_feature_list_by_tile(feature_list, tile)
        logging.info("Export finished.")

    # Export tileset.json for each timestamp
    writer.export_tileset(tileset)
    logging.info("End computation.\n")


def produce_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList, tiler: TilesetTiler, args=None):
    """
    The function `produce_3DTiles_sunlight` merges all tiles to create one TileSet, computes 3D Tiles
    sunlight, and then computes and exports aggregates based on different date groups.

    :param sun_datas_list: A list of sun data objects. Each sun data object contains information about
    the position of the sun at a specific time and location
    :type sun_datas_list: pySunlight.SunDatasList
    :param tiler: The `tiler` parameter is an instance of the `TilesetTiler` class. It is used to
    perform operations related to tiling and merging tilesets
    :type tiler: TilesetTiler
    :param args: The 'args' parameter is an optional argument that can be passed to the function. It is
    used to provide additional configuration or settings to the function
    """
    # Merge all tiles to create one TileSet
    tileset = tiler.read_and_merge_tilesets()

    # Compute and export Sunlight for each timestamp
    for i, sun_datas in enumerate(sun_datas_list):
        logging.info(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps - {sun_datas.dateStr}.")

        # Initialize each path
        CURRENT_OUTPUT_DIRECTORY = Utils.get_output_directory_for_timestamp(tiler.get_output_dir(), sun_datas.dateStr)
        # writer = CsvWriter(CURRENT_OUTPUT_DIRECTORY)
        writer = TileWriter(CURRENT_OUTPUT_DIRECTORY, tiler)
        writer.create_directory()

        compute_3DTiles_sunlight(tileset, sun_datas, writer)

    if args.with_aggregate:
        aggregator = AggregatorControllerInBatchTable(tiler.get_output_dir(), tiler)

        # We group all dates to compute aggreate on different group (by day and by month)
        dates = SunlightToTiler.get_dates_from_sun_datas_list(sun_datas_list)
        dates_by_month_and_days = Utils.group_dates_by_month_and_days(dates)
        num_of_tiles = len(tileset.get_root_tile().get_children())
        aggregator.compute_and_export(num_of_tiles, dates_by_month_and_days)


def parse_command_line():
    """
    The function `parse_command_line` is a Python function that uses the `argparse` module to parse
    command line arguments and returns the parsed arguments.
    :return: The function `parse_command_line` returns the parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Light pre-calculation based on real data (urban data and sun position) with 3DTiles.')
    parser.add_argument('--start-date', '-s', dest='start_date', type=int, help='Start date of sunlight computation. Ex : --start-date 403224', required=True)
    parser.add_argument('--end-date', '-e', dest='end_date', type=int, help='End date of sunlight computation. Ex : --end-date 403248', required=True)  # type: ignore
    parser.add_argument('--with-aggregate', dest='with_aggregate', action='store_true', help='Add aggregate to 3DTiles export.')

    # Set Logging level for the whole application
    parser.add_argument('--log-level', '-log', dest='log_level', default='WARNING', choices=logging._nameToLevel.keys(), help='Provide logging level. Ex : --log-level DEBUG, default=WARNING')

    return parser.parse_known_args()[0]


def main():
    args = parse_command_line()

    logging.basicConfig(level=args.log_level, format='[%(asctime)s] [%(levelname)s] %(message)s')

    sunParser = pySunlight.SunEarthToolsParser()
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", args.start_date, args.end_date)

    # Read all tiles in a folder using command line arguments
    tiler = TilesetTiler()
    tiler.parse_command_line()

    produce_3DTiles_sunlight(sunParser.getSunDatas(), tiler, args)


if __name__ == '__main__':
    main()
