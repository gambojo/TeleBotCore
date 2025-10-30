import os
from aiogram.types import FSInputFile
from core.bot.logging import logger


class ImageManager:
    """
    Менеджер для работы с изображениями (локальными и CDN)
    Параметры: use_local - использовать локальные файлы или CDN
    Возвращает: экземпляр ImageManager
    Пример: images = ImageManager(use_local=True)
    """

    def __init__(self, use_local: bool = True):
        self.use_local = use_local
        self.cache: dict[str, FSInputFile] = {}
        self.local = {"banner": "core/display/images/telefather.jpg"}
        self.cdn = {"banner": "https://cdn.example.com/banner.jpg"}

    def get_banner(self, plugin: str | None = None) -> FSInputFile | str:
        """
        Получает баннер для плагина или общий баннер
        Параметры: plugin - имя плагина для специфичного баннера
        Возвращает: FSInputFile | str - файл изображения или URL
        Пример: banner = images.get_banner('VPN')
        """
        if self.use_local:
            if plugin:
                plugin_path = f"assets/images/banner_{plugin}.jpg"
                if os.path.exists(plugin_path):
                    return self._get_file(plugin_path)
                logger.info(f"[ImageManager] Fallback to default banner for plugin '{plugin}'")
            return self._get_file(self.local["banner"])

        if plugin:
            return f"https://cdn.example.com/banner_{plugin}.jpg"
        return self.cdn["banner"]

    def _get_file(self, path: str) -> FSInputFile | str:
        if path in self.cache:
            return self.cache[path]
        if not os.path.exists(path):
            logger.warning(f"[ImageManager] Missing image: {path}")
            return "—"
        file = FSInputFile(path)
        self.cache[path] = file
        return file
