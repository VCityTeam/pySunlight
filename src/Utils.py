import logging
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
