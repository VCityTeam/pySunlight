from typing import List

import numpy as np
from py3dtilers.Common import FeatureList
from py3dtilers.TilesetReader.TilesetReader import TilesetReader

import Utils
from Converters import TilerToSunlight

# The Aggregator class is a placeholder for a more complex implementation thaht allow to compute aggregats individually.


class Aggregator():
    def __init__(self):
        """
        The function initializes variables and vectors for storing aggregate results and uses a
        vectorized function to compute percentages on numpy arrays.
        """
        self.name = None

        # Store all aggregate result
        self.daily_result = []
        self.monthly_result = []

        # Vectorise a function to use on each value of a numpy array
        self.vectorised_compute_percent = np.vectorize(Utils.compute_percent)

    def get_name(self):
        return self.name

    def get_normalized_daily_result(self):
        """
        The function "get_normalized_daily_result" returns None.
        :return: None
        """
        return None

    def get_normalized_monthly_result(self):
        """
        The function "get_normalized_monthly_result" returns None.
        :return: None
        """
        return None

    def initialize_count(self):
        """
        The function initializes two empty lists, `daily_result` and `monthly_result`.
        """
        self.daily_result = []
        self.monthly_result = []

    def compute_hourly_for(self, feature_list: FeatureList, hours: List[str]):
        """
        The function initializes exposure percentages with only one allocation if the daily result is
        empty.

        :param feature_list: A list of features that need to be allocated hours for
        :type feature_list: FeatureList
        :param hours: The "hours" parameter is a list of strings representing the hours of the day
        :type hours: List[str]
        """
        # Initialize exposure percentages with only one allocation
        if len(self.daily_result) == 0:
            self.daily_result = np.zeros(len(feature_list))

    def add_daily_result_to_monthly_result(self):
        """
        The function adds the daily result to the monthly result.
        """
        if 0 < len(self.monthly_result):
            self.monthly_result = np.add(self.daily_result, self.monthly_result)
        else:
            self.monthly_result = self.daily_result

        self.daily_result = []


# The ExposureAggregator class is a subclass of the Aggregator class that compute exposure percent for each feature.
class ExposureAggregator(Aggregator):
    def get_name(self):
        return "ExposurePercent"

    def get_normalized_daily_result(self):
        """
        The function `get_normalized_daily_result` converts all values in `self.daily_result` to
        percentages.
        :return: the daily result, which has been converted to percentages.
        """
        return self.vectorised_compute_percent(self.daily_result, whole=self.num_hours_by_day)

    def get_normalized_monthly_result(self):
        """
        The function returns the normalized monthly result by computing the percentage using the monthly
        result and the number of hours in each month.
        :return: the result of the `vectorised_compute_percent` method, which is being called with the
        `self.monthly_result` as the input and `whole=self.num_hours_by_month` as an additional
        argument.
        """
        return self.vectorised_compute_percent(self.monthly_result, whole=self.num_hours_by_month)

    def initialize_count(self):
        """
        The function initializes the count of hours by day and by month.
        """
        super().initialize_count()

        self.num_hours_by_day = 0
        self.num_hours_by_month = 0

    def compute_hourly_for(self, feature_list: FeatureList, hours: List[str]):
        """
        The function computes the hourly exposure for each feature in a feature list and adds it to the
        daily result.

        :param feature_list: A list of features. Each feature has a batchtable_data attribute that
        contains information about the feature, including the 'bLighted' attribute which represents
        whether the feature is lighted or not
        :type feature_list: FeatureList
        :param hours: The "hours" parameter is a list of strings representing the hours of the day. It
        is used to calculate the number of hours in a day for normalization purposes
        :type hours: List[str]
        """
        super().compute_hourly_for(feature_list, hours)

        # Count hours to normalize daily result
        self.num_hours_by_day = len(hours)

        for feature_index, feature in enumerate(feature_list):
            exposure = (int)(feature.batchtable_data['bLighted'])
            self.daily_result[feature_index] += exposure

    def add_daily_result_to_monthly_result(self):
        """
        The function adds the daily result to the monthly result and resets the daily counter.
        """
        super().add_daily_result_to_monthly_result()

        # Append hour count to month and reset the counter to normalize monthly result
        self.num_hours_by_month += self.num_hours_by_day
        self.num_hours_by_day = 0


# The `OccludeAggregator` class is a subclass of the `Aggregator` class that compute occlude percent for each feature.
class OccludeAggregator(Aggregator):
    def __init__(self, root_directory: str, num_of_tiles: int):
        """
        This function initializes an object with a root directory, number of tiles, and optional
        arguments.

        :param root_directory: The root directory is the main directory where the code will look for the
        files and folders it needs to process. It is a string that specifies the path to the root
        directory
        :type root_directory: str
        :param num_of_tiles: The parameter `num_of_tiles` represents the number of tiles in the tileset.
        It is an integer value that specifies the total number of tiles in the tileset
        :type num_of_tiles: int
        """
        Aggregator.__init__(self)

        # Reference all tiles, because a feature can occlude a feature from a different tile
        self.root_directory = root_directory
        self.num_of_tiles = num_of_tiles
        self.tileset_reader = TilesetReader()

        # Allow to use feature id as identifier and avoid to touch daily result structure
        self.index_by_feature_id = dict()

        self.num_of_feature_by_day = 0
        self.num_of_feature_by_month = 0

    def get_name(self):
        return "OccludePercent"

    def get_normalized_daily_result(self):
        """
        The function returns the normalized daily result by computing the percentage of the monthly
        result.
        :return: the result of calling the method `vectorised_compute_percent` with the arguments
        `self.monthly_result` and `whole=self.num_of_feature_by_day`.
        """
        return self.vectorised_compute_percent(self.daily_result, whole=self.num_of_feature_by_day, precision_digits=5)

    def get_normalized_monthly_result(self):
        """
        The function returns the normalized monthly result using vectorized computation.
        :return: the result of the vectorised_compute_percent method, which is the normalized monthly
        result.
        """
        return self.vectorised_compute_percent(self.monthly_result, whole=self.num_of_feature_by_month, precision_digits=5)

    def initialize_count(self):
        """
        The function initializes count variables and a dictionary for indexing feature IDs.
        """
        super().initialize_count()

        self.num_of_feature_by_day = 0
        self.num_of_feature_by_month = 0
        self.index_by_feature_id = dict()

    def compute_hourly_for(self, feature_list, hours):
        """
        The function computes the hourly occlusion of features in a given feature list by other features
        in a tileset.

        :param feature_list: The `feature_list` parameter is a list of features. Each feature is a
        dictionary that contains information about a specific feature, such as its ID, batchtable data,
        and occulting ID
        :param hours: The `hours` parameter is a list of time intervals or timestamps for which the
        computation is being performed. It represents the specific hours or time periods for which the
        code is calculating the hourly results
        """
        super().compute_hourly_for(feature_list, hours)

        # Initialize identifier
        if len(self.index_by_feature_id) == 0:
            for i, feature in enumerate(feature_list):
                self.index_by_feature_id[feature.batchtable_data['id']] = i

        for hour in hours:
            # Loop in all tiles, because a feature can occlude a feature from a different tile
            for tile_index in range(0, self.num_of_tiles):
                # Load tile corresponding to a given hour
                other_feature_list = TilerToSunlight.get_feature_list_from_tile_index_at(tile_index, self.tileset_reader, self.root_directory, hour)

                self.num_of_feature_by_day += len(other_feature_list)

                # Increase occlude amount of the current feature list
                for feature in other_feature_list:
                    occultingId = feature.batchtable_data['occultingId']
                    if not occultingId:
                        continue

                    daily_index = self.index_by_feature_id[occultingId]
                    self.daily_result[daily_index] += 1

    def add_daily_result_to_monthly_result(self):
        """
        The function adds the daily result to the monthly result and resets the daily counter.
        """
        super().add_daily_result_to_monthly_result()

        # Append hour count to month and reset the counter to normalize monthly result
        self.num_of_feature_by_month += self.num_of_feature_by_day
        self.num_of_feature_by_day = 0


# The `OccludeAmountAggregator` class is a subclass of the `Aggregator` class that compute occlude amount for each feature.
class OccludeAmountAggregator(Aggregator):
    def __init__(self, root_directory: str, num_of_tiles: int):
        """
        This function initializes an object with a root directory, number of tiles, and optional
        arguments.

        :param root_directory: The root directory is the main directory where the code will look for the
        files and folders it needs to process. It is a string that specifies the path to the root
        directory
        :type root_directory: str
        :param num_of_tiles: The parameter `num_of_tiles` represents the number of tiles in the tileset.
        It is an integer value that specifies the total number of tiles in the tileset
        :type num_of_tiles: int
        """
        Aggregator.__init__(self)

        # Reference all tiles, because a feature can occlude a feature from a different tile
        self.root_directory = root_directory
        self.num_of_tiles = num_of_tiles
        self.tileset_reader = TilesetReader()

        # Allow to use feature id as identifier and avoid to touch daily result structure
        self.index_by_feature_id = dict()

    def get_name(self):
        return "OccludeAmount"

    def get_normalized_daily_result(self):
        """
        The function returns the normalized daily result by computing the percentage of the monthly
        result.
        :return: the result of calling the method `vectorised_compute_percent` with the arguments
        `self.monthly_result` and `whole=self.num_of_feature_by_day`.
        """
        return self.daily_result

    def get_normalized_monthly_result(self):
        """
        The function returns the normalized monthly result using vectorized computation.
        :return: the result of the vectorised_compute_percent method, which is the normalized monthly
        result.
        """
        return self.monthly_result

    def initialize_count(self):
        """
        The function initializes count variables and a dictionary for indexing feature IDs.
        """
        super().initialize_count()

        self.index_by_feature_id = dict()

    def compute_hourly_for(self, feature_list, hours):
        """
        The function computes the hourly occlusion of features in a given feature list by other features
        in a tileset.

        :param feature_list: The `feature_list` parameter is a list of features. Each feature is a
        dictionary that contains information about a specific feature, such as its ID, batchtable data,
        and occulting ID
        :param hours: The `hours` parameter is a list of time intervals or timestamps for which the
        computation is being performed. It represents the specific hours or time periods for which the
        code is calculating the hourly results
        """
        super().compute_hourly_for(feature_list, hours)

        # Initialize identifier
        if len(self.index_by_feature_id) == 0:
            for i, feature in enumerate(feature_list):
                self.index_by_feature_id[feature.batchtable_data['id']] = i

        for hour in hours:
            # Loop in all tiles, because a feature can occlude a feature from a different tile
            for tile_index in range(0, self.num_of_tiles):
                # Load tile corresponding to a given hour
                other_feature_list = TilerToSunlight.get_feature_list_from_tile_index_at(tile_index, self.tileset_reader, self.root_directory, hour)

                # Increase occlude amount of the current feature list
                for feature in other_feature_list:
                    occultingId = feature.batchtable_data['occultingId']
                    if not occultingId:
                        continue

                    daily_index = self.index_by_feature_id[occultingId]
                    self.daily_result[daily_index] += 1
