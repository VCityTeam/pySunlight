# Sunlight wrapped in python
import pySunlight
# Convert py3DTilers type in Sunlight types
import SunlightConverter
from SunlightResult import SunlightResult

# Profile Libraries
import sys
import cProfile
import pstats

def export_results(sunlight_results):
    """
    The function exports sunlight results to an OBJ file format.
    
    :param sunlight_results: The `sunlight_results` parameter is a list of lists. Each inner list
    represents the results for a specific timestamp. Each timestamp contains a list of `triangle_result`
    objects
    """
    OUTPUT_DIRECTORY = "./datas/tests/"

    objExporter = pySunlight.SunlightObjExporter()
    objExporter.createOutputDirectory(OUTPUT_DIRECTORY)

    for timestamp_results in sunlight_results:
        # Reset vertex count between each timestamp, because it's a new file
        objExporter.resetVertexCount()

        for triangle_result in timestamp_results:
            objExporter.exportResult(triangle_result.dateStr, triangle_result.bLighted, triangle_result.origin_triangle, OUTPUT_DIRECTORY)


def produce_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList):
    """
    The function `produce_3DTiles_sunlight` takes a list of sun data and computes the sunlight
    visibility for each triangle in a tileset, storing the results in a list of `SunlightResult`
    objects, and then exports the results.
    
    :param sun_datas_list: A list of sun data objects. Each sun data object contains information about
    the direction of the sun and the date for which the sunlight needs to be computed
    :type sun_datas_list: pySunlight.SunDatasList
    """
    print("Load triangles from tileset...")
    triangle_soup = SunlightConverter.get_triangle_soup_from_tileset()
    print(f"Successfully load {len(triangle_soup)} triangles !")

    # Convert octet to Mega octet
    print(f"We are using {len(triangle_soup) * sys.getsizeof(pySunlight.Triangle) / 1024 / 1024} Mo for our triangles.")

    # Start profiling
    cp = cProfile.Profile()
    cp.enable()

    results = []
    
    for i, sun_datas in enumerate(sun_datas_list):
        result = list()

        print(f"Computes Sunlight {i + 1} on {len(sun_datas_list)} timestamps for {sun_datas.dateStr}.")

        for triangle in triangle_soup:
            # Don't compute intersection if the triangle is already looking at the ground
            if not pySunlight.isFacingTheSun(triangle, sun_datas.direction):
                # Associate shadow with the same triangle, because there's
                # nothing blocking it but itself
                result.append(SunlightResult(sun_datas.dateStr, False, triangle, triangle.getId()))
                continue

            ray = pySunlight.constructRay(triangle, sun_datas.direction)

            # Sort result by impact distance (from near to far)
            triangleRayHits = pySunlight.checkIntersectionWith(ray, triangle_soup)

            if 0 < len(triangleRayHits):
                # We consider the first triangle to be blocking
                nearest_hit_triangle = triangleRayHits[0].triangle
                result.append(SunlightResult(sun_datas.dateStr, False, triangle, nearest_hit_triangle.getId()))

            # Triangle is in plain sunlight
            else:
                result.append(SunlightResult(sun_datas.dateStr, True, triangle, ""))

        results.append(result)

        print(f"End computation")

    # Stop profiling
    cp.disable()
    p = pstats.Stats(cp)
    # Sort stats by time and print them
    p.sort_stats('tottime').print_stats()

    print(f"Exporting result...")
    export_results(results)
    print(f"Export finished.")


def main():
    sunParser = pySunlight.SunEarthToolsParser()
    # 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
    # 403248 corresponds to 2016-01-01 at 24:00 in 3DUSE.
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403248)
    produce_3DTiles_sunlight(sunParser.getSunDatas())


if __name__ == '__main__':
    main()
