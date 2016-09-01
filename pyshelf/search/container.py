from pyshelf.search.update_manager import UpdateManager
from pyshelf.search.manager import Manager
from pyshelf.search.connection import Connection
from pyshelf.search.sorter import Sorter


class Container(object):
    def __init__(self, logger, elastic_config):
        self.config = elastic_config
        self.logger = logger

        # Services
        self._update_manager = None
        self._manager = None
        self._connection = None
        self._sorter = None

    @property
    def update_manager(self):
        """
            Returns:
                pyshelf.search.update_manager.UpdateManager
        """
        if not self._update_manager:
            self._update_manager = UpdateManager(self.logger, self.connection)

        return self._update_manager

    @property
    def manager(self):
        """
            Returns:
                pyshelf.search.manager.Manager
        """
        if not self._manager:
            self._manager = Manager(self)

        return self._manager

    @property
    def sorter(self):
        """
            Returns:
                pyshelf.search.sorter.Sorter
        """
        if not self._sorter:
            self._sorter = Sorter()

        return self._sorter

    @property
    def connection(self):
        """
            Returns:
                pyshelf.search.connection.Connection
        """
        if not self._connection:
            self._connection = Connection(
                self.config["connectionString"],
                self.config.get("accessKey"),
                self.config.get("secretKey"),
                self.config.get("region"),
                self.config.get("upperSearchResultLimit")
            )

        return self._connection
