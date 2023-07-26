# Sunlight wrapped in python
import pySunlight
# Convert py3DTilers type in Sunlight types
import SunlightConverter
from SunlightResult import SunlightResult

import Utils

# def export_results(sunlight_results, tileset_tree: TilesetTree):
#     """
#     The function exports sunlight results to an OBJ file format.

#     :param sunlight_results: The `sunlight_results` parameter is a list of lists. Each inner list
#     represents the results for a specific timestamp. Each timestamp contains a list of `triangle_result`
#     objects
#     """
#     # OUTPUT_DIRECTORY = "datas/export/"

#     # objExporter = pySunlight.SunlightObjExporter()
#     # objExporter.createOutputDirectory(OUTPUT_DIRECTORY)

#     # for i, timestamp_results in enumerate(sunlight_results):
#     #     print(f"Export {i + 1} on {len(sunlight_results)}.")

#     #     # Reset vertex count between each timestamp, because it's a new file
#     #     objExporter.resetVertexCount()

#     #     for triangle_result in timestamp_results:
#     #         objExporter.exportResult(triangle_result.dateStr, triangle_result.bLighted, triangle_result.origin_triangle, OUTPUT_DIRECTORY)

#     for i, timestamp_results in enumerate(sunlight_results):
#         print(f"Export {i + 1} on {len(sunlight_results)}.")

#         for triangle_result in timestamp_results:
#             pass

#     # # Transform building feature to triangle feature
#     # for root_node in tileset_tree.root_nodes:
#     #     # # Build a feature with a triangle level
#     #     triangles_as_features = []
#     #     for j, sunlight_result in enumerate(timestamp_results):
#     #         triangle = sunlight_result.origin_triangle

#     #         triangle_as_feature = Feature(triangle.getId())
#     #         triangle_as_feature.geom.triangles.append(list(triangle))
#     #         triangles_as_features.append(triangle_as_feature)

#     #     root_node.feature_list = FeatureList(triangles_as_features)

#     # # Export final result
#     # tileset = tiler.create_tileset_from_feature_list(tileset_tree)
#     # print("Write")
#     # tileset.write_as_json(tiler.get_output_dir())


def produce_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList):
    """
    The function `produce_3DTiles_sunlight` takes a list of sun data and computes the sunlight
    visibility for each triangle in a tileset, storing the results in a list of `SunlightResult`
    objects, and then exports the results.

    :param sun_datas_list: A list of sun data objects. Each sun data object contains information about
    the direction of the sun and the date for which the sunlight needs to be computed
    :type sun_datas_list: pySunlight.SunDatasList
    """

    # Read and merge inputs tileset
    tileset = SunlightConverter.read_tileset()

    for i, sun_datas in enumerate(sun_datas_list):
        print(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps - {sun_datas.dateStr}.")
        results = []

        # Loop in tileset.json
        all_tiles = tileset.get_root_tile().get_children()
        for j, tile in enumerate(all_tiles):
            result = list()

            print(f"Load triangles from tile {j} ...")
            triangles = SunlightConverter.get_triangle_soup_from_tile(tile)
            print(f"Successfully load {len(triangles)} tiles !")

            Utils.print_memory_size_in_megabyte(triangle)

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

            results.append(result)

        print("End computation.")

        # print("Exporting result...")
        # export_results(results, tileset_tree)
        # print("Export finished.")


def main():
    sunParser = pySunlight.SunEarthToolsParser()
    # 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
    # 403248 corresponds to 2016-01-01 at 24:00 in 3DUSE.
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403248)

    produce_3DTiles_sunlight(sunParser.getSunDatas())


if __name__ == '__main__':
    main()
