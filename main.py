import pySunlight
import SunlightConverter


def main():
    print("Load triangles from tileset...")
    triangle_soup = SunlightConverter.get_triangle_soup_from_tileset()
    print(f"Successfully load {len(triangle_soup)} triangles !")

    sunDirection = pySunlight.Vec3d(0, 0, 0)

    for triangle in triangle_soup:
        ray = pySunlight.constructRay(triangle, sunDirection)
        triangleRayHits = pySunlight.checkIntersectionWith(ray, triangle_soup)

        if 0 < len(triangleRayHits):
            print(f"Triangle {triangle.getId()} is blocked by {triangleRayHits[0].triangle.getId()}")

        # else:
        #     print(f"Triangle {triangle.getId()} is in light")

if __name__ == '__main__':
    main()
