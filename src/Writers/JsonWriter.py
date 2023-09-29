import json
from pathlib import Path

from py3dtilers.Common import Feature, FeatureList

from .Writer import Writer

# The JsonWriter class is a subclass of the Writer class and export 3DTiles batch table in a json.


class JsonWriter(Writer):
    def export_feature_list_by_tile(self, feature_list: FeatureList, tile_index: int):
        super().export_feature_list_by_tile(feature_list, tile_index)

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

    def get_feature_list_from_tile(self, tile_index: int, root_directory: str):
        feature_list = FeatureList()

        path_str = str(Path(root_directory, f"{tile_index}.json"))

        with open(path_str, 'r') as file:
            batch_table = json.load(file)

            # Recreate feature list from json files
            for id, batch_table_content in batch_table.items():
                feature = Feature(id)

                for key, value in batch_table_content.items():
                    feature.add_batchtable_data(key, value)

                feature_list.append(feature)

        return feature_list
