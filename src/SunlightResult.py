from pySunlight import Triangle


# The SunlightResult class store the results of a sunlight analysis.
class SunlightResult:
    def __init__(self, date_str: str, bLighted: bool, origin_triangle: Triangle, occulting_id: str):
        self.date_str = date_str
        self.bLighted = bLighted
        self.origin_triangle = origin_triangle
        self.occulting_id = occulting_id

    def __str__(self):
        return f"SunlightResult(date_str={self.date_str}, bLighted={self.bLighted}, origin_triangle={self.origin_triangle.getId()}, occulting_id={self.occulting_id})"
