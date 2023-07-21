import pySunlight
import SunlightConverter


def main():
    triangle_soup = SunlightConverter.get_triangle_soup_from_tileset()

    origin = pySunlight.Vec3d(0, 0, 0)
    direction = pySunlight.Vec3d(0, 10, 0)
    ray = pySunlight.Ray(origin, direction)

    pySunlight.checkIntersectionWith(ray, triangle_soup)


if __name__ == '__main__':
    main()
