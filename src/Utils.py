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
