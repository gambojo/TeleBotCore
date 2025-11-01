import tomllib
from pathlib import Path
from typing import Dict, Any


class VersionManager:
    """
    Менеджер для работы с версиями проекта
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._metadata = self._get_metadata()
            self._initialized = True

    def _get_metadata(self) -> Dict[str, Any]:
        """Читает метаданные из pyproject.toml"""
        try:
            pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            return {
                "title": data["project"]["name"],
                "version": data["project"]["version"],
                "author": data["project"]["authors"][0]["name"],
                "email": data["project"]["authors"][0]["email"]
            }

        except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
            return {
                "title": "telebotcore",
                "version": "1.0.0",
                "author": "Agamov Gamid",
                "email": "gamaefremov@gmail.com"
            }

    @property
    def title(self) -> str:
        return self._metadata["title"]

    @property
    def version(self) -> str:
        return self._metadata["version"]

    @property
    def author(self) -> str:
        return self._metadata["author"]

    @property
    def email(self) -> str:
        return self._metadata["email"]

    def get_info(self) -> Dict[str, Any]:
        """Возвращает полную информацию о версии"""
        return self._metadata.copy()
