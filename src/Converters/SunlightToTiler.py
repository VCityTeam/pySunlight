from py3dtilers.Common import FeatureList
from typing import List
from SunlightResult import SunlightResult
import pySunlight
import numpy as np
from py3dtilers.Common.feature import Feature

# This file convert Sunlight type to py3DTilers type


def convert_vec3_to_numpy(vec3: pySunlight.Vec3d):
    """
    The function converts a pySunlight.Vec3d object to a numpy array.

    :param vec3: The parameter `vec3` is of type `pySunlight.Vec3d`, which is a vector class
    representing a 3-dimensional vector
    :type vec3: pySunlight.Vec3d
    :return: a NumPy array containing the x, y, and z components of the input Vec3d object.
    """
    return np.array([vec3.getX(), vec3.getY(), vec3.getZ()])


def convert_to_tiler_triangle(triangle: pySunlight.Triangle):
    """
    The function `convert_to_tiler_triangle` takes a `pySunlight.Triangle` object and converts its
    vertices to a list of numpy arrays forming a triangle.

    :param triangle: The parameter `triangle` is of type `pySunlight.Triangle`. It represents a triangle
    object from the `pySunlight` library
    :type triangle: pySunlight.Triangle
    :return: a list of three numpy arrays, where each array represents a vertex of the triangle.
    """
    a = convert_vec3_to_numpy(triangle.a)
    b = convert_vec3_to_numpy(triangle.b)
    c = convert_vec3_to_numpy(triangle.c)

    return [a, b, c]


def convert_to_feature(triangle: pySunlight.Triangle):
    """
    The function converts a triangle object from the pySunlight library into a feature object with a
    triangle geometry in the py3DTiler library.

    :param triangle: The parameter "triangle" is of type pySunlight.Triangle
    :type triangle: pySunlight.Triangle
    :return: a `Feature` object.
    """
    triangle_as_feature = Feature(triangle.getId())

    # Set geometry
    tiler_triangle = convert_to_tiler_triangle(triangle)
    triangle_as_feature.geom.triangles.append([tiler_triangle])

    return triangle_as_feature


def convert_to_feature_list_with_triangle_level(sunlight_results: List[SunlightResult]):
    """
    The function takes a list of SunlightResult objects, converts each origin_triangle into a feature,
    and adds batch table data to each feature before returning the list of features.

    :param sunlight_results: The parameter `sunlight_results` is expected to be a list of
    `SunlightResult` objects
    :type sunlight_results: List[SunlightResult]
    :return: a FeatureList object containing the converted triangles with additional batch table data.
    """
    triangles_as_features = FeatureList()
    for result in sunlight_results:
        triangle_as_feature = convert_to_feature(result.origin_triangle)

        # Record result in batch table
        triangle_as_feature.add_batchtable_data('date', result.date_str)
        triangle_as_feature.add_batchtable_data('bLighted', result.bLighted)
        triangle_as_feature.add_batchtable_data('occultingId', result.occulting_id)

        triangles_as_features.append(triangle_as_feature)

    return triangles_as_features
