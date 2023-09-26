import json

from py3dtilers.Common import FeatureList
from py3dtiles import Tile

from pathlib import Path
from .Writer import Writer

# The JsonWriter class is a subclass of the Writer class and export 3DTiles batch table in a json.


class JsonWriter(Writer):
    def export_feature_list_by_tile(self, feature_list: FeatureList, tile: Tile, tile_index: int):
        super().export_feature_list_by_tile(feature_list, tile, tile_index)

        formated_results = dict()

        # Gather all batch table content around a feature
        for feature in feature_list:
            formated_results[feature.get_id()] = dict()

            for k, v in feature.get_batchtable_data().items():
                formated_results[feature.get_id()][k] = v

        # Store all result corresponding to one tile
        path_str = str(Path(self.directory, f"{tile_index}.json"))
        with open(path_str, 'w', newline='') as file:
            json.dump(formated_results, file)
