import logging
from pathlib import Path

from py3dtilers.Common import FeatureList
from py3dtiles import Tile, TileSet

# The Writer class is a placeholder for a code implementation of Sunlight result export.


class Writer():
    def __init__(self, directory):
        self.directory = directory

    def set_directory(self, directory: str):
        """
        The function sets the directory attribute of an object to the specified directory.

        :param directory: The "directory" parameter is a string that represents the path to a directory
        :type directory: str
        """
        self.directory = directory

    def set_args(self, args):
        """
        The function sets the value of the "args" attribute of an object.

        :param args: The "args" parameter is a variable that can be used to pass in arguments to a
        method or function. It can be of any data type and can be used to provide additional information
        or values that the method or function needs to perform its task
        """
        self.args = args

    def create_directory(self):
        """
        The function "create_directory" is defined but does not contain any code.
        """
        pass

    def export_tileset(self, tileset: TileSet):
        """
        The function exports a tileset to a specified directory, but returns an error if the directory
        is not defined.

        :param tileset: The `tileset` parameter is an instance of the `TileSet` class. It represents a
        collection of tiles that can be used to create a map or a game level
        :type tileset: TileSet
        :return: nothing (None).
        """
        if self.directory is None:
            logging.error("Output Directory is undefined. Can't export...")
            return

    def export_feature_list_by_tile(self, feature_list: FeatureList, tile: Tile, tile_index: int):
        """
        The function exports a feature list by tile, but only if the output directory is defined.

        :param feature_list: A list of features that you want to export. It could be a list of strings,
        objects, or any other data type that represents the features you want to export
        :type feature_list: FeatureList
        :param tile: The "tile" parameter is an object of the "Tile" class. It represents a specific
        tile or section of a larger area
        :type tile: Tile
        :return: nothing (None).
        """
        if self.directory is None:
            logging.error("Output Directory is undefined. Can't export...")
            return

# The FileWriter class is a subclass of the Writer class and export 3DTiles batch table in one file (json, csv...).


class FileWriter(Writer):
    def __init__(self, directory, file_name):
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
        with open(str(path), 'w'):
            pass
