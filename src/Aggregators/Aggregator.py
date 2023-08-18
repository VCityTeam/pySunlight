from typing import List

import numpy as np
from py3dtilers.Common import FeatureList

import Utils


# The Aggregator class is a placeholder for a more complex implementation thaht allow to compute aggregats individually.
class Aggregator():
    def __init__(self, id: str):
        """
        The function initializes an object with an ID and stores aggregate results, and also vectorizes
        a function to use on each value of a numpy array.

        :param id: The `id` parameter is a string that represents the identifier for an instance of the
        class. It is used to uniquely identify each instance and can be used for various purposes, such
        as tracking or referencing the instance
        :type id: str
        """
        self.id = id

        # Store all aggregate result
        self.daily_result = []
        self.monthly_result = []

        # Vectorise a function to use on each value of a numpy array
        self.vectorised_compute_percent = np.vectorize(Utils.compute_percent)

    def get_id(self):
        """
        The function returns the id of an object.
        :return: The method `get_id` is returning the value of the `id` attribute of the object.
        """
        return self.id

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
