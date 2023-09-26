import csv
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
        super().create_directory()

        path = self.get_path()

        # Create a new empty file to append in export tile
        with open(str(path), 'w'):
            pass

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile: Tile, tile_index: int):
        """
        The function exports a batch table by tile and appends the results to a CSV file.

        :param feature_list: A list of features that you want to export
        :type feature_list: FeatureList
        :param tile: The "tile" parameter is an instance of the "Tile" class. It represents a specific
        tile that is being processed
        :type tile: Tile
        """
        super().export_feature_list_by_tile(feature_list, tile, tile_index)

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
