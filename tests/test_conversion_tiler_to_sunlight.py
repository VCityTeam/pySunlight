import unittest
import numpy as np

from src.Converters import TilerToSunlight
from src import pySunlight
# py3DTiles
from py3dtiles.bounding_volume_box import BoundingVolumeBox
from py3dtiles.tile import Tile, TileContent
# py3DTilers
from py3dtilers.Common import Feature


class TestConversionTilerToSunlight(unittest.TestCase):
    def test_numpy_to_vec3(self):
        intarray = np.array([1, 2, 3])
        intvec3 = pySunlight.Vec3d(1, 2, 3)

        resultint = TilerToSunlight.convert_numpy_to_vec3(intarray)

        dvec3 = pySunlight.Vec3d(1.247, 2.4, 3.124534)

        resultd = TilerToSunlight.convert_numpy_to_vec3(np.array([1.247, 2.4, 3.124534]))

        self.assertTrue(intvec3 == resultint and dvec3 == resultd, "Wrong numpy to vec3 conversion")

    def test_convert_to_triangle(self):
        tiler_triangle = [np.array([1, 2, 3]), np.array([2, 3, 1]), np.array([3, 2, 1])]
        sunlight_triangle = pySunlight.Triangle(pySunlight.Vec3d(1, 2, 3), pySunlight.Vec3d(2, 3, 1), pySunlight.Vec3d(3, 2, 1), "test", "test")
        result = TilerToSunlight.convert_to_sunlight_triangle(tiler_triangle, "test", "test")

        self.assertTrue(result.getNormal() == sunlight_triangle.getNormal() and result.getBarycenter() == sunlight_triangle.getBarycenter())

    def test_convert_to_bounding_box(self):
        aa_bounding_box = BoundingVolumeBox()
        aa_bounding_box.set_from_mins_maxs([1, 1, 1, 5, 5, 5])

        oriented_bounding_box = BoundingVolumeBox()
        oriented_bounding_box.set_from_list([0, 0, 0, 0.5, 0.5, 0, -0.5, 0.5, 0, 0, 0, 1])

        # pySunlight.AABB(min, max, id, tile_name)
        aabb_sunlight = pySunlight.AABB(pySunlight.Vec3d(1, 1, 1), pySunlight.Vec3d(5, 5, 5), "test", "test")
        aabb_from_oriented = pySunlight.AABB(pySunlight.Vec3d(-1, -1, -1), pySunlight.Vec3d(1, 1, 1), "test", "test")

        result = TilerToSunlight.convert_to_bounding_box(aa_bounding_box, "test", "test")
        result_from_oriented = TilerToSunlight.convert_to_bounding_box(oriented_bounding_box, "test1", "test")

        self.assertTrue(aabb_sunlight.max == result.max and aabb_sunlight.min == result.min, "Wrong conversion from AABB")
        self.assertTrue(aabb_from_oriented.max == result_from_oriented.max and aabb_from_oriented.min == result_from_oriented.min, "Wrong conversion from oriented bounding box")

    def test_add_triangle_from_feature(self):
        triangle_soup = pySunlight.TriangleSoup()

        feature = Feature("test")
        feature.geom.triangles.append([[np.array([1, 2, 3]), np.array([2, 3, 1]), np.array([3, 2, 1])], [np.array([2, 2, 2]), np.array([1, 3, 1]), np.array([4.5, 2, 1])]])

        # To build a Tile from scratch, you need a TileContent
        tile = Tile()
        tile.set_content(TileContent())
        tile.set_content_uri("test")

        TilerToSunlight.add_triangles_from_feature(triangle_soup, feature, tile, 1)

        triangle2 = triangle_soup.pop()
        triangle = triangle_soup.pop()

        self.assertEqual(triangle.a.getX(), 1, "Triangle is corrupted")
        self.assertEqual(triangle2.c.getX(), 4.5, "Triangle is corrupted")
        self.assertEqual(triangle.m_id, "Tile-test__Feature-test__Triangle-0", "Wrong triangle id")
        self.assertEqual(triangle2.m_id, "Tile-test__Feature-test__Triangle-1", "Wrong triangle id")
