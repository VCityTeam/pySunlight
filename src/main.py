from typing import List
import logging

from py3dtiles.tile import Tile
from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtilers.Common import GeometryNode, FeatureList, ObjWriter
from py3dtilers.Common.tileset_creation import FromGeometryTreeToTileset

# Sunlight wrapped in python
import pySunlight
# Convert py3DTilers type in Sunlight types
import SunlightConverter
from SunlightResult import SunlightResult
import Utils


def export_result_by_tile(sunlight_results: List[SunlightResult], tile: Tile, output_directory: str, args=None):
    """
    The function exports the results of sunlight calculations for each triangle in a tile to an output
    directory.

    :param sunlight_results: A list of SunlightResult objects. Each SunlightResult object represents the
    result of a sunlight calculation for a specific triangle
    :type sunlight_results: List[SunlightResult]
    :param tile: The `tile` parameter is an object of the `Tile` class. It represents a specific tile in
    a tileset
    :type tile: Tile
    :param output_directory: The `output_directory` parameter is a string that specifies the directory
    where the exported tile will be saved
    :type output_directory: str
    :param args: The `args` parameter is an optional argument that can be passed to the function. It is
    used to provide additional configuration or settings that may be needed for the export process. The
    specific purpose and structure of the `args` parameter would depend on the context and requirements
    of the code that calls this function
    """
    # Build a feature with a triangle level
    triangles_as_features = FeatureList()
    for result in sunlight_results:
        triangle_as_feature = SunlightConverter.convert_to_feature(result.origin_triangle)

        # Record result in batch table
        triangle_as_feature.add_batchtable_data('date', result.dateStr)
        triangle_as_feature.add_batchtable_data('bLighted', result.bLighted)
        triangle_as_feature.add_batchtable_data('blockerId', result.blockerId)

        triangles_as_features.append(triangle_as_feature)

    obj_writer = ObjWriter()
    node = GeometryNode(triangles_as_features)
    node.set_node_features_geometry(args)

    # Export Tile
    tile_centroid = tile.get_transform()[12:15]
    offset = FromGeometryTreeToTileset._FromGeometryTreeToTileset__transform_node(node, args, tile_centroid, obj_writer=obj_writer)
    FromGeometryTreeToTileset._FromGeometryTreeToTileset__create_tile(node, offset, None, output_directory)


def produce_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList, tileset: TilesetTiler, output_directory: str, args=None):
    """
    The function `produce_3DTiles_sunlight` takes a list of sun data and computes the sunlight
    visibility for each triangle in a tileset, storing the results in a list of `SunlightResult`
    objects, and then exports the results.

    :param sun_datas_list: A list of sun data objects. Each sun data object contains information about
    the direction of the sun and the date for which the sunlight needs to be computed
    :type sun_datas_list: pySunlight.SunDatasList
    """
    for i, sun_datas in enumerate(sun_datas_list):
        logging.info(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps - {sun_datas.dateStr}.")

        valid_directory_name = sun_datas.dateStr.replace(":", "__")
        CURRENT_OUTPUT_DIRECTORY = f"{output_directory}/{valid_directory_name}"

        # Reset the counter, because it could be incremented with the previous timestamp loop
        FromGeometryTreeToTileset.tile_index = 0

        # Loop in tileset.json
        all_tiles = tileset.get_root_tile().get_children()
        for j, tile in enumerate(all_tiles):
            result = []

            logging.debug(f"Load triangles from tile {j} ...")
            triangles = SunlightConverter.get_triangle_soup_from_tile(tile)
            logging.info(f"Successfully load {len(triangles)} tiles !")

            Utils.log_memory_size_in_megabyte(triangles)

            for triangle in triangles:
                # Don't compute intersection if the triangle is already looking at the ground
                if not pySunlight.isFacingTheSun(triangle, sun_datas.direction):
                    # Associate shadow with the same triangle, because there's
                    # nothing blocking it but itself
                    result.append(SunlightResult(sun_datas.dateStr, False, triangle, triangle.getId()))
                    continue

                ray = pySunlight.constructRay(triangle, sun_datas.direction)

                # Sort result by impact distance (from near to far)
                triangleRayHits = pySunlight.checkIntersectionWith(ray, triangles)

                if 0 < len(triangleRayHits):
                    # We consider the first triangle to be blocking
                    nearest_hit_triangle = triangleRayHits[0].triangle
                    result.append(SunlightResult(sun_datas.dateStr, False, triangle, nearest_hit_triangle.getId()))

                # Triangle is in plain sunlight
                else:
                    result.append(SunlightResult(sun_datas.dateStr, True, triangle, ""))

            logging.info("Exporting result...")
            export_result_by_tile(result, tile, CURRENT_OUTPUT_DIRECTORY, args)
            logging.info("Export finished.")

        # Export tileset.json for each timestamp
        tileset.write_as_json(CURRENT_OUTPUT_DIRECTORY)
        logging.info("End computation.\n\n")


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
