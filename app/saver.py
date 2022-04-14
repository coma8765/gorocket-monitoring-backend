import csv
import os
from typing import Dict, Any, List

from .transport import InputData


class Saver:
    """Saver for data
    Save in folder env `LOG_FOLDER`, default "logs"
    """

    def __init__(self):
        self.file = open(f"{os.getenv('LOG_FOLDER', 'logs')}/data_{len(self.older_files())}.csv", "w", newline="")

        fieldnames = list(InputData.schema()["properties"].keys())
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
        self.writer.writeheader()

    def save(self, data: Dict[str, Any]):
        self.writer.writerow(data)
        self.file.flush()

    def close(self):
        self.file.close()

    @staticmethod
    def older_files() -> List[str]:
        return list(filter(lambda x: x.startswith("data_"), os.listdir(os.getenv('LOG_FOLDER', 'logs'))))
