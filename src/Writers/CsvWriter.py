import csv

from py3dtilers.Common import FeatureList
from py3dtiles import Tile

from .Writer import FileWriter

# The CsvWriter class is a subclass of the FileWriter class and export 3DTiles batch table in a csv.


class CsvWriter(FileWriter):
    def __init__(self, directory, file_name="output.csv"):
        super().__init__(directory, file_name)

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
