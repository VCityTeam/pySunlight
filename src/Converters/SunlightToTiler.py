from typing import List

import numpy as np
from py3dtilers.Common import FeatureList
from py3dtilers.Common.feature import Feature

from .. import pySunlight

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


def convert_to_feature_list_with_triangle_level(triangle_soup: pySunlight.TriangleSoup):
    """
    The function converts a pySunlight.TriangleSoup object into a feature list, where each triangle is represented
    as a feature.

    :param triangle_soup: The parameter `triangle_soup` is of type `pySunlight.TriangleSoup`. It is
    a data structure that represents a collection of triangles supported by Sunlight.
    :type triangle_soup: pySunlight.TriangleSoup
    :return: a FeatureList object containing the triangles converted to features.
    """
    triangles_as_features = FeatureList()

    # Convert and add each geometry
    for triangle in triangle_soup:
        triangle_as_feature = convert_to_feature(triangle)
        triangles_as_features.append(triangle_as_feature)

    return triangles_as_features


def record_result_in_batch_table(feature: Feature, date_str: str, bLighted: bool, occulting_id: str):
    """
    The function `record_result_in_batch_table` adds data to a batch table for a given feature.

    :param feature: The "feature" parameter is an object of the "Feature" class. It is used to represent
    a specific feature or entity in your code
    :type feature: Feature
    :param date_str: A string representing the date of the record
    :type date_str: str
    :param bLighted: The parameter "bLighted" is a boolean value that indicates whether the feature is
    lighted or not
    :type bLighted: bool
    :param occulting_id: The `occulting_id` parameter is a string that represents the ID of the
    occulting object
    :type occulting_id: str
    """
    feature.add_batchtable_data('date', date_str)
    feature.add_batchtable_data('bLighted', bLighted)
    feature.add_batchtable_data('occultingId', occulting_id)


def record_results_from_collision(results: FeatureList, ray_hits_by_index: dict, date_str: str):
    for feature_index, feature in enumerate(results):
        # Already record value
        if 0 < len(feature.get_batchtable_data()):
            continue

        # Triangle is hidden
        if feature_index in ray_hits_by_index:
            occultingId = ray_hits_by_index[feature_index].triangle.getId()
            record_result_in_batch_table(feature, date_str, False, occultingId)

        # Triangle in sunlight
        else:
            record_result_in_batch_table(feature, date_str, True, "")


def get_dates_from_sun_datas_list(sun_datas_list: pySunlight.SunDatasList):
    """
    The function "get_dates_from_sun_datas_list" takes a list of SunDatas objects and returns a list of
    their corresponding date strings.

    :param sun_datas_list: A list of SunDatas objects
    :type sun_datas_list: SunDatasList
    :return: a list of dates extracted from the `SunDatasList` object.
    """
    dates = []
    for sun_datas in sun_datas_list:
        dates.append(sun_datas.dateStr)

    return dates
