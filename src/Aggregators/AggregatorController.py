from typing import List
from pathlib import Path
import numpy as np
import logging
from py3dtilers.TilesetReader.TilesetReader import TilesetReader
from Writers import TileWriter
from py3dtilers.Common import FromGeometryTreeToTileset
import Utils
from Converters import TilerToSunlight

# The AggregatorControllerInBatchTable class is used for aggregating data in a batch table.


class AggregatorControllerInBatchTable():
    def __init__(self, root_directory: str, args=None):
        """
        The function initializes an object with a root directory and optional arguments.

        :param root_directory: The `root_directory` parameter is a string that represents the root
        directory of 3DTiles Sunlight export.
        :type root_directory: str
        :param args: The `args` parameter is an optional argument that can be passed to the `__init__`
        method. It is a variable that can hold any additional arguments or parameters that you may want
        to pass to the class constructor. It is typically used to customize the behavior of the class or
        provide additional information
        """
        self.root_directory = root_directory
        self.args = args

    def export_aggregate_for_an_entire_day(self, batch_key: str, aggregate: List[int], day: List[str], tile_index: int):
        """
        The function add aggregate data in the batch table of a tile for an entire day with a given batch 
        table key.

        :param batch_key: The `batch_key` parameter is a string that represents the key for the batch
        table data. It is used to identify the specific data that is being added to each feature in the
        tile
        :type batch_key: str
        :param aggregate: The `aggregate` parameter is a list of integers representing the aggregate
        values for each feature. Each integer in the list corresponds to a feature in the `feature_list`
        :type aggregate: List[int]
        :param day: The `day` parameter is a list of strings representing the hours of the day. Each
        string in the list represents a specific hour
        :type day: List[str]
        :param tile_index: The `tile_index` parameter represents the index of the tile within the
        tileset that you want to export the aggregate data for. It is used to retrieve the specific tile
        from the tileset and perform operations on it
        :type tile_index: int
        """
        tileset_reader = TilesetReader()

        for hour in day:
            # Reset tile index, because it increase at each export
            FromGeometryTreeToTileset.tile_index = tile_index

            # Load tile corresponding to a given hour
            CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(self.root_directory, hour)
            tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
            tile = tileset.get_root_tile().get_children()[tile_index]
            feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

            # Set aggregate value
            for i, feature in enumerate(feature_list):
                current_exposure = aggregate[i]
                feature.add_batchtable_data(batch_key, current_exposure)

            tile_writer = TileWriter(CURRENT_DIRECTORY, self.args)
            tile_writer.export_feature_list_by_tile(feature_list, tile)

    def compute_and_export_exposure(self, num_of_tiles: int, dates_by_month_and_days: List[List[str]]):
        """
        The function `compute_and_export_exposure` computes the aggregate exposure of sunlight on each tile
        based on the provided dates and exports the results.

        :param num_of_tiles: The parameter `num_of_tiles` represents the total number of tiles that need
        to be processed for sunlight exposure computation. It will be used to loop in each timestamp folder
        to search the correct tiles
        :type num_of_tiles: int
        :param dates_by_month_and_days: The parameter `dates_by_month_and_days` is a list of lists that
        represents the dates for each month and day. Each inner list contains strings representing the
        dates for a specific month. For example, if `dates_by_month_and_days` is `[['2022-01-01', '202
        :type dates_by_month_and_days: List[List[str]]
        """
        tileset_reader = TilesetReader()

        # Vectorise a function to use on each value of a nump array
        vectorised_compute_percent = np.vectorize(Utils.compute_percent)

        # We compute exposure on each tile
        for tile_index in range(0, num_of_tiles):
            logging.info(f"Compute aggregate of tile : {Utils.compute_percent(tile_index, num_of_tiles)}%...")

            # Monthly exposure computation
            monthlyExposureByFeature = []
            for i, months in enumerate(dates_by_month_and_days):
                logging.info(f"Loop in month {i + 1} on {len(dates_by_month_and_days)}")

                num_hours_by_month = 0

                # Daily exposure computation
                for j, day in enumerate(months):
                    num_hours_by_day = len(day)
                    num_hours_by_month += num_hours_by_day
                    dailyExposureByFeature = []

                    for hour in day:
                        CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(self.root_directory, hour)

                        # Extract feature list from the current 3DTiles Sunlight
                        tileset = tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
                        tile = tileset.get_root_tile().get_children()[tile_index]
                        feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

                        for feature_index, feature in enumerate(feature_list):
                            # Initialize exposure percentages with only one allocation
                            if len(dailyExposureByFeature) == 0:
                                dailyExposureByFeature = np.zeros(len(feature_list))

                            exposure = (int)(feature.batchtable_data['bLighted'])
                            dailyExposureByFeature[feature_index] += exposure

                    # Export daily result after looping on each hour
                    logging.debug(f"Exporting daily exposure percent {Utils.compute_percent(j, len(months))}% ...")

                    # Convert all value in percent
                    dailyExposurePercent = vectorised_compute_percent(dailyExposureByFeature, whole=num_hours_by_day)
                    self.export_aggregate_for_an_entire_day('dailyExposurePercent', dailyExposurePercent, day, tile_index)
                    del dailyExposurePercent

                    logging.debug(f"Exporting daily exposure percent completed.")

                    # Sum all exposure by day
                    if 0 < len(monthlyExposureByFeature):
                        monthlyExposureByFeature = np.add(dailyExposureByFeature, monthlyExposureByFeature)
                    else:
                        monthlyExposureByFeature = dailyExposureByFeature

                # Export monthly result after looping on each day
                logging.debug(f"Exporting monthly exposure percent...")

                # Convert all value in percent
                monthlyExposureByFeature = vectorised_compute_percent(monthlyExposureByFeature, whole=num_hours_by_month)
                for day in months:
                    self.export_aggregate_for_an_entire_day('monthlyExposurePercent', monthlyExposureByFeature, day, tile_index)

                logging.debug(f"Exporting monthly exposure percent completed.")

            logging.info("End computation.")

    def compute_and_export(self, num_of_tiles: int, dates_by_month_and_days: List[List[str]]):
        self.compute_and_export_exposure()
