from pySunlight import Triangle


# The SunlightResult class store the results of a sunlight analysis.
class SunlightResult:
    def __init__(self, dateStr: str, bLighted: bool, origin_triangle: Triangle, blockerId: str):
        self.dateStr = dateStr
        self.bLighted = bLighted
        self.origin_triangle = origin_triangle
        self.blockerId = blockerId

    def __str__(self):
        return f"SunlightResult(dateStr={self.dateStr}, bLighted={self.bLighted}, origin_triangle={self.origin_triangle.getId()}, blockerId={self.blockerId})"
