import pySunlight

# ====================================== Test Types Constructors ======================================
# Test vector3 construction
v = pySunlight.Vec3d(0, 4, 1)
print(f"Vector : {v}")

# Test ray construction
origin = pySunlight.Vec3d(0, 0, 0)
direction = pySunlight.Vec3d(0, 10, 0)
ray = pySunlight.Ray(origin, direction)
print(f"Ray from ({ray.origin}) to ({ray.direction})")

# Test triangle construction
triangle = pySunlight.Triangle(v, v, v, "Id", "Tile Name")
print(f"Triangle {triangle.getId()} in {triangle.getTileName()}")

# Test bounding box intersection
min = pySunlight.Vec3d(-10, -10, -10)
max = pySunlight.Vec3d(10, 10, 10)
boundingBox = pySunlight.AABB(min, max, "Id", "TileName")
print(f"Bounding Box {boundingBox.getId()} of {boundingBox.getTileName()}")

# Test sun earth parser
sunParser = pySunlight.SunEarthToolsParser()
# 403224 corresponds to 2016-01-01 at 00:00 in 3DUSE.
# 403248 corresponds 2016-01-01 at 24:00 in 3DUSE.
sunParser.loadSunpathFile("datas/AnnualSunPath_Lyon.csv", 403224, 403248)
print(f"Expect 24 sun positions : {sunParser.getSunDatas().size()}")

# ====================================== Test pySunlight Raytracing API ======================================
# Test IsFacingTheSun
triangle = pySunlight.Triangle(v, v, v, "Id", "Tile Name")
sunDirection = pySunlight.Vec3d(0, 0, 0)
if pySunlight.isFacingTheSun(triangle, sunDirection):
    print(f"Triangle {triangle.getId()} is facing the sun")

# Test passing a vector of triangle/bounding boxes
tmp = pySunlight.Vec3d(-10, -10, -10)
boundingBoxes = pySunlight.BoundingBoxes()
boundingBoxes.push_back(pySunlight.AABB(tmp, tmp, "", ""))
boundingBoxes.push_back(pySunlight.AABB(tmp, tmp, "", ""))
boundingBoxes.push_back(pySunlight.AABB(tmp, tmp, "", ""))
pySunlight.checkIntersectionWith(ray, boundingBoxes)

triangleSoup = pySunlight.TriangleSoup()
triangleSoup.push_back(triangle)
triangleSoup.push_back(triangle)
triangleSoup.push_back(triangle)
pySunlight.checkIntersectionWith(ray, triangleSoup)
