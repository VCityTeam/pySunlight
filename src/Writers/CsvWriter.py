import csv
from pathlib import Path

from py3dtilers.Common import FeatureList

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

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile_index: int):
        """
        The function exports a batch table by tile and appends the results to a CSV file.

        :param feature_list: A list of features that you want to export
        :type feature_list: FeatureList
        """
        super().export_feature_list_by_tile(feature_list, tile_index)

        # Append all result / batch table content in the same csv
        path_str = str(self.get_path())
        firstline = False

        # Checking if we're on the first line and writing the header if we are
        with open(path_str, 'r', newline='') as file:
            if len(file.readlines()) < 1:
                firstline = True

        with open(path_str, 'a', newline='') as file:
            writer = csv.writer(file)

            if firstline:
                writer.writerow(["tile;feature;triangle;date;lighted;occludingTile;occludingFeature;occludingTriangle"])

            # Append each batch table result
            for feature in feature_list:

                # Extracting actual ids from the weird stuff that they've been doing
                ID = feature.get_id()
                TileId = ID[ID.find("/") + 1:ID.find(".b3dm")]
                FeatureID = ID[ID.find("Feature") + 8:ID.find("__Triangle")]
                TriangleID = ID[ID.find("Triangle") + 9:]

                output = f'{TileId};{FeatureID};{TriangleID};'

                values = [value for key, value in feature.batchtable_data.items()]

                for i in range(len(values) - 1):
                    output += f'{values[i]};'

                if values[1]:
                    output += ';;'
                else:
                    ID = values[2]
                    TileId = ID[ID.find("/") + 1:ID.find(".b3dm")]
                    FeatureID = ID[ID.find("Feature") + 8:ID.find("__Triangle")]
                    TriangleID = ID[ID.find("Triangle") + 9:]

                    output += f'{TileId};{FeatureID};{TriangleID}'

                writer.writerow([output.strip()])
