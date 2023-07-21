# Sunlight wrapped in python
import pySunlight
# Convert py3DTilers type in Sunlight types
import SunlightConverter
from SunlightResult import SunlightResult
import sys


def produce_3DTiles_sunlight(sun_datas_list: pySunlight.SunDatasList):
    print("Load triangles from tileset...")
    triangle_soup = SunlightConverter.get_triangle_soup_from_tileset()
    print(f"Successfully load {len(triangle_soup)} triangles !")

    # Convert octet to Mega octet
    print(f"We are using {len(triangle_soup) * sys.getsizeof(pySunlight.Triangle) / 64} Mo for our triangles.")

    results = list()

    for sun_datas in sun_datas_list:
        for triangle in triangle_soup:

            # Don't compute intersection if the triangle is already looking at the ground
            if not pySunlight.isFacingTheSun(triangle, sun_datas.direction):
                # Associate shadow with the same triangle, because there's
                # nothing blocking it but itself
                results.append(SunlightResult(sun_datas.dateStr, False, triangle.getId()))
                continue

            ray = pySunlight.constructRay(triangle, sun_datas.direction)

            # Sort result by impact distance (from near to far)
            triangleRayHits = pySunlight.checkIntersectionWith(ray, triangle_soup)

            if 0 < len(triangleRayHits):
                # We consider the first triangle to be blocking
                nearest_hit_triangle = triangleRayHits[0].triangle
                results.append(SunlightResult(sun_datas.dateStr, False, nearest_hit_triangle.getId()))

            # Triangle is in plain sunlight
            else:
                results.append(SunlightResult(sun_datas.dateStr, True, ""))


def main():
    sunParser = pySunlight.SunEarthToolsParser()
    # 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
    # 403248 corresponds 2016-01-01 at 24:00 in 3DUSE.
    sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403248)
    produce_3DTiles_sunlight(sunParser.getSunDatas())


if __name__ == '__main__':
    main()
