from itertools import groupby
import logging
from pympler import asizeof
from pySunlight import SunDatasList


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


def group_dates_by_month_and_days(sun_datas_list: SunDatasList):
    """
    The function `group_dates_by_month_and_days` takes a list of `SunDatas` objects, extracts the dates
    from them, sorts the dates, and then groups them by month and days.

    :param sun_datas_list: A list of SunDatas objects, where each object has a dateStr attribute
    representing a date in the format "YYYY-MM-DD:HHMM"
    :type sun_datas_list: SunDatasList
    :return: a list of lists, where each inner list represents a group of dates. The dates are grouped
    first by month and then by day.
    """
    dates = []
    for sun_datas in sun_datas_list:
        dates.append(sun_datas.dateStr)

    # sort the dates
    dates.sort()

    # Group by month
    grouped_dates = [list(g) for k, g in groupby(dates, key=lambda x: x.split('-')[1])]
    # Group by days
    grouped_dates = [list(g) for k, g in groupby(grouped_dates[0], key=lambda x: x.replace(':', '-').split('-')[2])]

    return grouped_dates


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
