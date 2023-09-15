import unittest
from src.pySunlight import Vec3d, Triangle, TriangleSoup, SunDatas, checkIntersectionWith, constructRay

class TestIntersection(unittest.TestCase):
    # Detecting collision with itself relating to the issue : https://github.com/VCityTeam/pySunlight/issues/5
    def test_collision_with_the_same_triangle(self):
        triangle = Triangle(Vec3d(1844824.875335, 5174043.500452, 167.460002), Vec3d(1844824.250335, 5174044.000452, 167.460002), Vec3d(1844824.750335, 5174043.500452, 167.460002))
        sun_datas = SunDatas("2016-01-01:0800", Vec3d(1888857.649890, 5136065.174273, 12280.013599), Vec3d(0.748839, -0.630358, 0.204667))
        ray = constructRay(triangle, sun_datas.direction)

        triangle_soup = TriangleSoup()
        triangle_soup.push_back(triangle)

        self.assertTrue(len(checkIntersectionWith(ray, triangle_soup)) == 0, 'Detect collision with the triangle from the origin of the ray')