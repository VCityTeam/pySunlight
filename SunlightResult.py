from pySunlight import Triangle

class SunlightResult:
    def __init__(self, dateStr: str, bLighted: bool, origin_triangle: Triangle, blockerId: str):
        self.dateStr = dateStr
        self.bLighted = bLighted
        self.origin_triangle = origin_triangle
        self.blockerId = blockerId
