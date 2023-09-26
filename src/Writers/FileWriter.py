import logging
from pathlib import Path

from .Writer import Writer

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
