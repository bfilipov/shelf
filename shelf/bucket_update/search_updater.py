import shelf.artifact_key_filter as filters
from shelf.bucket_update.artifact_metadata_updater import ArtifactMetadataUpdater
from shelf.cloud.cloud_exceptions import BucketNotFoundError
from pprint import pformat


class SearchUpdater(object):
    """
        Responsible from updating the search metadata based on our
        source of truth the "cloud" which right now at least will
        be S3.
    """
    def __init__(self, container):
        """
            Args:
                container(shelf.bucket_update.container.Container)
        """
        self.container = container
        self.bucket_container = self.container.bucket_container
        self.chunk_size = self.container.config.get("chunkSize")
        self.logger = self.container.logger
        self.update_manager = self.container.search_container.update_manager

    def load_path_list(self):
        """
            Loads a list of artifact paths from the cloud.  This does
            NOT include metadata or special private data.

            Returns:
                List(basestring)
        """
        with self.bucket_container.create_cloud_storage() as storage:
            artifact_list = storage.get_directory_contents("", True)
            path_list = filters.to_path_list(artifact_list)
            path_list = filters.directories(path_list)
            path_list = filters.all_private(path_list)

        return path_list

    def update(self):
        """
            Runs the actual update.  This will loop through a list of
            artifact paths, load the metadata, and then update it in
            bulk into the "search layer" which in our case is elasticsearch.
        """
        path_list = self.load_path_list()

        self.logger.info("Starting to process {0} artifact's metadata".format(len(path_list)))
        all_id_list = []
        for chunk_list in self._chunk(path_list):
            bulk_update = {}
            self.logger.info("Processing chunk: {0}".format(pformat(chunk_list)))
            for path in chunk_list:
                self.add_artifact_metadata(path, bulk_update)

            self.update_manager.bulk_update(bulk_update)
            all_id_list = all_id_list + bulk_update.keys()

        self.remove_unlisted_documents_per_bucket(all_id_list)

    def prune(self):
        """
            Loops through a list of artifact paths, compares them against
            the search index, and removes any indexes that no longer exist.
        """
        path_list = []

        try:
            path_list = self.load_path_list()
        except BucketNotFoundError:
            self.logger.info("Bucket wasn't found. Leaving path_list empty.")

        self.logger.info("Starting to collect {0} artifact's Elasticsearch ids.".format(len(path_list)))
        all_id_list = []

        for path in path_list:
            identity = self.container.resource_identity_factory \
                .from_cloud_identifier(path)
            all_id_list.append(identity.search)

        self.remove_unlisted_documents_per_bucket(all_id_list)

    def remove_unlisted_documents_per_bucket(self, all_id_list):
        """
            This function exists to log the removal of search documents.

            Args:
                all_id_list(List(basestring)): List containing all the
                    Elasticsearch ids that relate to artifacts in the bucket.
        """
        self.logger.info("Deleting anything in search that is not in this list {0}".format(pformat(all_id_list)))
        deleted = self.update_manager.remove_unlisted_documents_per_bucket(
                                                                        all_id_list,
                                                                        self.container.config["referenceName"]
                                                                    )
        self.logger.info("Update of reference name {0} has been completed. Deleted {1} documents.".format(
            self.container.config["referenceName"],
            deleted
        ))

    def add_artifact_metadata(self, path, bulk_update):
        """
            Takes a path for a particular artifact, gets the metadata
            for that artifact, and adds it to the bulk_update dictionary.

            I prefer to not return two things, so instead I just pass along
            the dictionary that the data needs to be added to.

            Args:
                path(basestring): Path to an artifact.  Not it's metadata
                bulk_update(dict(schemas/metadata.json)): A structure that stores an artifact's
                    metadata and keys it based off of their search identifier.
                    See shelf.resource_identifier.ResourceIdentifier for more
                    information about identifiers.
        """
        identity = self.container.resource_identity_factory \
            .from_cloud_identifier(path)
        updater = ArtifactMetadataUpdater(self.bucket_container, identity)
        updater.run()
        bulk_update[identity.search] = updater.metadata

    def _chunk(self, path_list):
        """
            A generate that will (with each yield) return the next
            chunk of artifact paths that should be processed
        """
        for index in range(0, len(path_list), self.chunk_size):
            yield path_list[index: index + self.chunk_size]
