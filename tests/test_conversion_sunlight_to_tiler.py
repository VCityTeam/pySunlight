import unittest
import numpy as np

from src.Converters import SunlightToTiler
from src import pySunlight

# py3DTilers
from py3dtilers.Common import Feature


class TestConversionSunlightToTiler(unittest.TestCase):
    def test_convert_vec3_to_numpy(self):
        intarray = np.array([1, 2, 3])
        intvec3 = pySunlight.Vec3d(1, 2, 3)

        resultint = SunlightToTiler.convert_vec3_to_numpy(intvec3)

        darray = np.array([1.247, 2.4, 3.124534123456789])
        dvec3 = pySunlight.Vec3d(1.247, 2.4, 3.124534123456789)

        resultd = SunlightToTiler.convert_vec3_to_numpy(dvec3)

        self.assertTrue(np.equal(intarray, resultint).all(), "Wrong conversion with int vec3")
        self.assertTrue(np.equal(darray, resultd).all(), "Wrong conversion with double vec3")

    def test_convert_to_tiler_triangle(self):
        tiler_triangle = [np.array([1, 2, 3]), np.array([2, 3, 1]), np.array([3, 2, 1])]
        sunlight_triangle = pySunlight.Triangle(pySunlight.Vec3d(1, 2, 3), pySunlight.Vec3d(2, 3, 1), pySunlight.Vec3d(3, 2, 1), "test", "test")
        result = SunlightToTiler.convert_to_tiler_triangle(sunlight_triangle)

        self.assertTrue(np.equal(result[0], tiler_triangle[0]).all())
        self.assertTrue(np.equal(result[1], tiler_triangle[1]).all())
        self.assertTrue(np.equal(result[2], tiler_triangle[2]).all())

    def test_convert_to_feature(self):
        sunlight_triangle = pySunlight.Triangle(pySunlight.Vec3d(1, 2, 3), pySunlight.Vec3d(2, 3, 1), pySunlight.Vec3d(3, 2, 1), "test", "test")

        feature = Feature("test")
        feature.geom.triangles.append([[np.array([1, 2, 3]), np.array([2, 3, 1]), np.array([3, 2, 1])]])

        result = SunlightToTiler.convert_to_feature(sunlight_triangle)

        self.assertTrue(np.equal(result.centroid, feature.centroid).all(), "Centroid shifted during conversion")
        self.assertTrue(np.equal(result.get_geom_as_triangles(), feature.get_geom_as_triangles()).all(), "Geometry error when converting")

    def test_convert_to_feature_list_with_triangle_level(self):
        sunlight_triangle = pySunlight.Triangle(pySunlight.Vec3d(1, 2, 3), pySunlight.Vec3d(2, 3, 1), pySunlight.Vec3d(3, 2, 1), "test", "test")

        feature = Feature("test")
        feature.geom.triangles.append([[np.array([1, 2, 3]), np.array([2, 3, 1]), np.array([3, 2, 1])]])

        triangle_soup = pySunlight.TriangleSoup()
        triangle_soup.push_back(sunlight_triangle)

        result = SunlightToTiler.convert_to_feature_list_with_triangle_level(triangle_soup)

        self.assertTrue(np.equal(result.features[0].centroid, feature.centroid).all(), "Centroid shifted during conversion")
        self.assertTrue(np.equal(result.features[0].get_geom_as_triangles(), feature.get_geom_as_triangles()).all(), "Geometry error when converting")
