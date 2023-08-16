import logging
from py3dtiles import TileSet
from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtilers.Common import FromGeometryTreeToTileset
from Converters import TilerToSunlight, SunlightToTiler
from SunlightResult import SunlightResult
from Writers import TileWriter
from Aggregator import AggregatorInBatchTable
import Utils
import pySunlight


def compute_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList, tileset: TileSet, root_directory: str, args=None):
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
    :param root_directory: The `root_directory` parameter is a string that specifies the directory
    where the computed results will be saved
    :type output_directory: str
    :param args: The `args` parameter is an optional argument that can be passed to the
    `compute_3DTiles_sunlight` function. It is not used within the function itself, so its purpose and
    expected value would depend on how the function is being used in the broader context of your code
    """
    for i, sun_datas in enumerate(sun_datas_list):
        logging.info(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps - {sun_datas.dateStr}.")

        CURRENT_OUTPUT_DIRECTORY = Utils.get_output_directory_for_timestamp(root_directory, sun_datas.dateStr)
        tile_writer = TileWriter(CURRENT_OUTPUT_DIRECTORY, args)

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
            tile_writer.export_feature_list_by_tile(feature_list, tile)
            logging.info("Export finished.")

        # Export tileset.json for each timestamp
        tile_writer.export_tileset(tileset)
        logging.info("End computation.\n")


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
    aggregator = AggregatorInBatchTable(output_directory, args)
    aggregator.compute_and_export(num_of_tiles, dates_by_month_and_days)


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
