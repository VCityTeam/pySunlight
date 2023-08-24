import logging
from pathlib import Path
from typing import List

from py3dtilers.Common import FromGeometryTreeToTileset
from py3dtilers.TilesetReader.TilesetReader import TilesetReader, TilesetTiler

from .. import Utils
from ..Converters import TilerToSunlight
from ..Writers import TileWriter
from .Aggregator import (
    Aggregator,
    ExposureAggregator,
    OccludeAggregator,
    OccludeAmountAggregator,
)

# The AggregatorControllerInBatchTable class is used for aggregating data in a batch table.


class AggregatorControllerInBatchTable():
    def __init__(self, root_directory: str, tiler: TilesetTiler):
        self.root_directory = root_directory
        self.tiler = tiler

        self.aggregators = []
        self.tileset_reader = TilesetReader()

    def export_results_for_an_entire_day(self, hours: List[str], tile_index: int, export_daily: bool):
        # Timestamp key to identify each result
        timestamp_key = 'daily' if export_daily else 'monthly'

        # Store each normalize result to avoid normalize at each call
        results = []
        for i, aggregator in enumerate(self.aggregators):
            result = aggregator.get_normalized_daily_result() if export_daily else aggregator.get_normalized_monthly_result()
            results.append(result)

        for hour in hours:
            # Reset tile index, because it increase at each export
            FromGeometryTreeToTileset.tile_index = tile_index

            # Load tile corresponding to a given hour
            CURRENT_DIRECTORY = Utils.get_output_directory_for_timestamp(self.root_directory, hour)
            tileset = self.tileset_reader.read_tileset(Path(CURRENT_DIRECTORY))
            tile = tileset.get_root_tile().get_children()[tile_index]
            feature_list = TilerToSunlight.get_feature_list_from_tile(tile)

            # Add all aggregators result
            for i, feature in enumerate(feature_list):
                for j, aggregator in enumerate(self.aggregators):
                    result = results[j][i]
                    feature.add_batchtable_data(f'{timestamp_key}{aggregator.get_name()}', result)

            tile_writer = TileWriter(CURRENT_DIRECTORY, self.tiler)
            tile_writer.export_feature_list_by_tile(feature_list, tile)

    def compute_and_export(self, num_of_tiles: int, dates_by_month_and_days: List[List[List[str]]]):
        self.aggregators: List[Aggregator] = [
            ExposureAggregator(),
            # OccludeAggregator(self.root_directory, num_of_tiles), OccludeAmountAggregator(self.root_directory, num_of_tiles)
        ]

        # We compute exposure on each tile
        for tile_index in range(0, num_of_tiles):
            logging.info(f"Compute aggregate of tile : {Utils.compute_percent(tile_index, num_of_tiles)}%...")

            # Initialize or reset computation
            for aggregator in self.aggregators:
                aggregator.initialize_count()

            # Monthly computation
            for i, months in enumerate(dates_by_month_and_days):
                logging.info(f"Loop in month {i + 1} on {len(dates_by_month_and_days)}")

                # Daily computation
                for j, day in enumerate(months):
                    # Hourly computation
                    for hour in day:

                        # Load tile corresponding to a given hour
                        feature_list = TilerToSunlight.get_feature_list_from_tile_index_at(tile_index, self.tileset_reader, self.root_directory, hour)

                        # Compute aggregate
                        for aggregator in self.aggregators:
                            aggregator.compute_hourly_for(feature_list, day)

                    # Export daily result after looping on each hour
                    logging.debug(f"Exporting daily result {Utils.compute_percent(j, len(months))}% ...")

                    for aggregator in self.aggregators:
                        self.export_results_for_an_entire_day(day, tile_index, True)

                    logging.debug(f"Exporting daily result completed.")

                    # Sum all aggregate by month
                    for aggregator in self.aggregators:
                        aggregator.add_daily_result_to_monthly_result()

                # Export monthly result after looping on each day
                logging.debug(f"Exporting monthly result...")

                # Convert all value in percent
                for day in months:
                    for aggregator in self.aggregators:
                        self.export_results_for_an_entire_day(day, tile_index, False)

                logging.debug(f"Exporting monthly result completed.")

            logging.info("End computation.")
