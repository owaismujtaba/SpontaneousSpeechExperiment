import json
from pathlib import Path
from typing import Optional


class AnnotationLoader:
    """
    Loads COCO-style caption annotations from per-image JSON files.

    Each JSON file is named  <image_filename>.json  and lives in ann_dir.
    The captions are stored as tags with name == "caption".

    An optional *translator* (see translator.py) can be passed to
    automatically translate every caption before returning it.
    """

    def __init__(self, ann_dir: Path, translator=None):
        self._ann_dir    = Path(ann_dir)
        self._translator = translator

    def captions(self, image_filename: str) -> list[str]:
        """
        Return the list of caption strings for *image_filename*.
        Captions are translated if a translator was supplied.
        Returns an empty list if the annotation file is missing or malformed.
        """
        ann_file = self._ann_dir / f"{image_filename}.json"
        if not ann_file.exists():
            return []
        try:
            with open(ann_file, encoding="utf-8") as fh:
                data = json.load(fh)
            raw = [
                tag["value"]
                for tag in data.get("tags", [])
                if tag.get("name") == "caption" and tag.get("value")
            ]
        except (json.JSONDecodeError, KeyError):
            return []

        if self._translator is not None:
            return self._translator.translate_list(raw)
        return raw
