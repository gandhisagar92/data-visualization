import json
import os
from typing import Any, Dict, List


class FileJsonStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.cache: Dict[str, List[Dict[str, Any]]] = {}

    def _load_file(self, name: str) -> List[Dict[str, Any]]:
        if name in self.cache:
            return self.cache[name]
        path = os.path.join(self.data_dir, f"{name}.json")
        if not os.path.exists(path):
            self.cache[name] = []
            return self.cache[name]
        with open(path, "r", encoding="utf-8") as f:
            self.cache[name] = json.load(f)
        return self.cache[name]

    def list_all(self, name: str) -> List[Dict[str, Any]]:
        return self._load_file(name)

    def find_by_attribute(self, name: str, attribute_type: str, attribute_id: Any) -> List[Dict[str, Any]]:
        items = self._load_file(name)
        matched: List[Dict[str, Any]] = []
        for item in items:
            if attribute_type in item and str(item.get(attribute_type)) == str(attribute_id):
                matched.append(item)
        return matched

    def get_by_id(self, name: str, primary_key: str, value: Any) -> Dict[str, Any] | None:
        items = self._load_file(name)
        for item in items:
            if str(item.get(primary_key)) == str(value):
                return item
        return None

