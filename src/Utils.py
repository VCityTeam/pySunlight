from py3dtilers.Common import FeatureList
import logging
from itertools import groupby
from typing import List

from pympler import asizeof


def log_memory_size_in_megabyte(object):
    """
    The function `log_memory_size_in_megabyte` log the memory size of an object in megabytes.

    :param object: The "object" parameter in the above code refers to any Python object for which you
    want to calculate and print its memory size in megabytes. This can be any variable, data structure,
    or instance of a class
    """

    # Convert octet to Mega octet
    full_size = asizeof.asizeof(object) / 1024 / 1024
    logging.debug(f"{object} is using {full_size} Mo.")


def group_dates_by_month_and_days(dates: List[str]):
    """
    The function groups a list of dates by month and then by day within each month.

    :param dates: A list of strings representing dates in the format "YYYY-MM-DD:HHMM"
    :type dates: List[str]
    :return: a list of lists of lists, where each inner list represents a month and contains sublists
    representing the days within that month. Each sublist contains the dates that fall on that day.
    """
    # sort the dates
    dates.sort()

    # Group by month
    grouped_dates = [list(g) for k, g in groupby(dates, key=lambda x: x.split('-')[1])]

    result = []
    for months in grouped_dates:
        result.append([list(g) for k, g in groupby(months, key=lambda x: x.replace(':', '-').split('-')[2])])

    return result


def get_output_directory_for_timestamp(root_directory: str, date: str):
    """
    The function `get_output_directory_for_timestamp` takes a root directory and a date string as input,
    and returns the resulting directory path.

    :param root_directory: The root directory is the base directory where you want to create the output
    directory. It should be a string representing the path to the root directory
    :type root_directory: str
    :param date: The `date` parameter is a string representing a timestamp
    :type date: str
    :return: a string that represents the output directory for a given timestamp.
    """
    # : are not supported in file / folder name
    valid_directory_name = date.replace(":", "__")
    return f"{root_directory}/{valid_directory_name}"


def compute_percent(part: int, whole: int, precision_digits=2):
    """
    The function `compute_percent` calculates the percentage of a part in relation to a whole, with an
    optional precision for the decimal places.

    :param part: The part parameter represents the value that is considered a part of the whole value.
    It is an integer value
    :type part: int
    :param whole: The total number or quantity that the part is a portion of
    :type whole: int
    :param precision_digits: The `precision_digits` parameter is an optional parameter that specifies
    the number of decimal places to round the percentage to. By default, it is set to 2, which means the
    percentage will be rounded to 2 decimal places. However, you can change this value to any positive
    integer to specify a, defaults to 2 (optional)
    :return: the percentage value of the part in relation to the whole, rounded to the specified number
    of precision digits.
    """
    percentage = (part / whole) * 100
    return round(percentage, 2)


def sort_batchtable_data_by_custom_order(feature_list: FeatureList):
    """
    The function sorts the batchtable data in a feature list based on a custom order.

    :param feature_list: The parameter `feature_list` is a list of objects of type `FeatureList`. Each
    object in the list represents a feature and contains a property called `batchtable_data`, which is a
    dictionary. The keys of the dictionary represent different attributes of the feature, and the values
    represent the corresponding data for
    :type feature_list: FeatureList
    """
    custom_order = ['id', 'date', 'bLighted', 'occultingId', 'dailyExposure', 'monthlyExposure']

    for feature in feature_list:
        # Ranges the key according to its order index or, if non-existent, at the end of the list
        feature.batchtable_data = dict(sorted(feature.get_batchtable_data().items(), key=lambda x: custom_order.index(x[0]) if x[0] in custom_order else len(custom_order)))
