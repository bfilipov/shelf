import pyproctor
from pyshelf.resource_identity import ResourceIdentity


class ResourceIdentityTest(pyproctor.TestBase):
    TEST_PATH = "/lol-test/artifact/blah1/blah2/blah3"

    def create(self):
        return ResourceIdentity(self.TEST_PATH)

    def test_bucket_name(self):
        identity = self.create()
        self.assertEqual("lol-test", identity.bucket_name)

    def test_path(self):
        identity = self.create()
        self.assertEqual("/blah1/blah2/blah3", identity.path)

    def test_cloud(self):
        self.assertEqual("/blah1/blah2/blah3", self.create().cloud)

    def test_search(self):
        self.assertEqual("abc0068b8b6cdd87550a4fc0cb5b7dc538c51c9ca50d5e5f9f4f2f08fc80e24e", self.create().search)
