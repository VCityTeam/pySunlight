import csv
import logging
from pathlib import Path

from py3dtilers.Common import FeatureList
from py3dtiles import Tile

from .Writer import Writer


# The CsvWriter class is a subclass of the Writer class and export 3DTiles batch table in a csv.
class CsvWriter(Writer):
    def __init__(self, directory, file_name="output.csv"):
        super().__init__(directory)

        self.file_name = file_name

    def get_path(self):
        """
        The function returns the path of a file by combining the directory and file name.
        :return: a Path object that represents the path to a file.
        """
        return Path(self.directory, self.file_name)

    def create_directory(self):
        """
        The function creates a directory and an empty file within that directory.
        :return: nothing (None).
        """
        super().create_directory()

        if self.directory is None:
            logging.error("Directory is undefined. Can't export...")
            return

        # Create directory
        path = self.get_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create a new empty file
        with open(str(path), 'w') as file:
            pass

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile: Tile):
        """
        The function exports a batch table by tile and appends the results to a CSV file.

        :param feature_list: A list of features that you want to export
        :type feature_list: FeatureList
        :param tile: The "tile" parameter is an instance of the "Tile" class. It represents a specific
        tile that is being processed
        :type tile: Tile
        """
        super().export_feature_list_by_tile(feature_list, tile)

        # Append all result / batch table content in the same csv
        path_str = str(self.get_path())
        with open(path_str, 'a', newline='') as file:
            writer = csv.writer(file)

            # Append each batch table result
            for feature in feature_list:
                output = f'{feature.get_id()};'

                for value in feature.batchtable_data.values():
                    output += f'{value};'

                writer.writerow([output.strip()])
