import logging

from py3dtilers.Common.feature import Feature, FeatureList
from py3dtilers.TilesetReader.TilesetReader import TilesetTiler
from py3dtilers.TilesetReader.tileset_tree import TilesetTree
from py3dtilers.Common import GeometryNode, FeatureList, ObjWriter
from py3dtilers.Common.tileset_creation import FromGeometryTreeToTileset

# Sunlight wrapped in python
import pySunlight
# Convert py3DTilers type in Sunlight types
import SunlightConverter
from SunlightResult import SunlightResult
import Utils


def convert_vec3_to_numpy(vec3: pySunlight.Vec3d):
    return [vec3.getX(), vec3.getY(), vec3.getZ()]


def convert_to_py3DTiler_triangle(triangle: pySunlight.Triangle):
    a = convert_vec3_to_numpy(triangle.a)
    b = convert_vec3_to_numpy(triangle.b)
    c = convert_vec3_to_numpy(triangle.c)

    return [a, b, c]


def export_results(sunlight_results):
    """
    The function exports sunlight results to an OBJ file format.

    :param sunlight_results: The `sunlight_results` parameter is a list of lists. Each inner list
    represents the results for a specific timestamp. Each timestamp contains a list of `triangle_result`
    objects
    """
    tiler = TilesetTiler()
    tiler.parse_command_line()
    tileset = tiler.read_and_merge_tilesets()
    tileset_tree = TilesetTree(tileset, tiler.tileset_of_root_tiles)

    for i, root_node in enumerate(tileset_tree.root_nodes):
        if (0 < i):
            break

        feature_list = root_node.feature_list
        all_triangles = []

        # Triangles list
        for feature in feature_list:
            triangles = feature.get_geom_as_triangles()
            all_triangles.extend(triangles)

        # Build a feature with a triangle level
        triangles_as_features = FeatureList()
        for j, triangle in enumerate(all_triangles):
            # Build a feature with a triangle level
            result = sunlight_results[j]
            id = result.origin_triangle.getId()

            # Transform feature to triangle level
            triangle_as_feature = Feature(id)
            triangle_as_feature.geom.triangles.append([triangle])

            # Record result in batch table
            triangle_as_feature.add_batchtable_data('date', result.dateStr)
            triangle_as_feature.add_batchtable_data('bLighted', result.bLighted)
            triangle_as_feature.add_batchtable_data('blockerId', result.blockerId)

            triangles_as_features.append(triangle_as_feature)

        # geometry_tree = GeometryTree()
        # tile.get_transform()[12:15]
        tree_centroid = tileset_tree.get_centroid()

        obj_writer = ObjWriter()
        node = GeometryNode(triangles_as_features)

        node.set_node_features_geometry(tiler.args)
        offset = FromGeometryTreeToTileset._FromGeometryTreeToTileset__transform_node(node, tiler.args, tree_centroid, obj_writer=obj_writer)
        FromGeometryTreeToTileset._FromGeometryTreeToTileset__create_tile(node, offset, None, tiler.get_output_dir())

    # Export final result
    tileset.write_as_json(tiler.get_output_dir())


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
        if (0 < i):
            return

        logging.info(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps - {sun_datas.dateStr}.")
        results = []

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
            export_results(result)
            logging.info("Export finished.")

            results.append(result)

        logging.info("End computation.")


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

    sunParser = pySunlight.SunEarthToolsParser()
    # 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
    # 403248 corresponds to 2016-01-01 at 24:00 in 3DUSE.
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403248)

    produce_3DTiles_sunlight(sunParser.getSunDatas())


if __name__ == '__main__':
    main()
