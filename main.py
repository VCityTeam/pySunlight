# Sunlight wrapped in python
import pySunlight
# Convert py3DTilers type in Sunlight types
import SunlightConverter
from SunlightResult import SunlightResult
import sys

def main():
    print("Load triangles from tileset...")
    triangle_soup = SunlightConverter.get_triangle_soup_from_tileset()
    print(f"Successfully load {len(triangle_soup)} triangles !")

    # Convert octet to Mega octet
    print(f"We are using {len(triangle_soup) * sys.getsizeof(pySunlight.Triangle) / 64} Mo for our triangles.")

    results = list()

    sunDirection = pySunlight.Vec3d(0, 0, 0)
    date = "2016-01-01"

    for triangle in triangle_soup:

        ray = pySunlight.constructRay(triangle, sunDirection)

        # Sort result by impact distance (from near to far)
        triangleRayHits = pySunlight.checkIntersectionWith(ray, triangle_soup)

        if 0 < len(triangleRayHits):
            # We consider the first triangle to be blocking
            nearestHitTriangle = triangleRayHits[0].triangle
            results.append(SunlightResult(date, False, nearestHitTriangle.getId()))

        # Triangle is in plain sunlight
        else:
            results.append(SunlightResult(date, True, ""))

if __name__ == '__main__':
    main()
