import logging
import os
from extractor.common import CloudService, Plugin
from typing import List, Optional

from extractor.common import camel_to_snake

logger = logging.getLogger(__name__)


class Extractor:
    """ """

    def __init__(
        self,
        service: CloudService,
        plugins: Optional[List[Plugin]] = None,
        **kwargs,
    ) -> None:
        """ """

        self._service = service
        self._plugins = []
        if plugins is None:
            plugins = []
        for plugin in plugins:
            self.add_plugin(plugin)

    @property
    def service(self):
        return self._service

    @property
    def plugins(self):
        return self._plugins

    def add_plugin(self, plugin):
        try:
            plugin.init(self)
        except AttributeError:
            pass

        self._plugins.append(plugin)

    def emit(self, event: str, *args, **kwargs):
        """ """
        event = camel_to_snake(event)
        func_name = f"on_{event}"

        for plugin in self._plugins:
            try:
                func = getattr(plugin, func_name)
                func(*args, **kwargs)
            except AttributeError:
                # specific handlerfunction doesn't exists
                try:
                    # try to call generic handler function
                    plugin.on(event, *args, **kwargs)
                except AttributeError:
                    # Plugin has no generic handler function
                    pass

        return self

    def acquire(self, username, password):
        """ """
        self.emit("extractor_start")

        #
        # Login / Acquire User
        #
        try:
            user = self._service.login(username, password)
        except Exception as e:
            self.emit("login_failure", e)
        else:
            self.emit("login_success", user)

            #
            # Acquire Folders
            #
            try:
                self.emit("before_acquire_folders")

                for folder in self._service.folders:
                    self.emit("folder_found", folder)

                self.emit("after_acquire_folders")
            except Exception as e:
                raise e

            #
            # Acquire Files
            #
            try:
                self.emit("before_acquire_files")

                for file in self._service.files:
                    self.emit("file_found", file)

                self.emit("after_acquire_files")
            except Exception as e:
                raise e

        self.emit("extractor_end")
