from tests.unit_test_base import UnitTestBase
from pyshelf.search_parser import SearchParser
from pyshelf.search.sort_type import SortType
from pyshelf.search.sort_flag import SortFlag
from pyshelf.search.type import Type as SearchType
import tests.metadata_utils as utils
from pyshelf.search_portal import SearchPortal
from mock import Mock


# CODE_REVIEW: Missing test cases
#
# ~= in the search twice. "version~=1.1~=blah"  <-- as messed up as that is.
# escaping ~ and *
# case insensitive sort_type/sort_flag (I know this doesn't exist yet)
# sending anything that is not a sort_type/sort_flag that is not the first field
# sort is an empty list/not provided at all
class SearchParseTest(UnitTestBase):
    def setUp(self):
        self.parser = SearchParser()
        self.portal = SearchPortal(Mock())

    def test_from_request(self):
        request_criteria = {
            "search": [
                "version~=1.1",
                "bob=bob",
                "dumb=dumbf*"
            ],
            "sort": [
                "version, VERSION, ASC",
                "bob, ASC"
            ]
        }
        expected = {
            "search": [
                {
                    "field": "version",
                    "value": "1.1",
                    "search_type": SearchType.VERSION
                },
                {
                    "field": "bob",
                    "value": "bob",
                    "search_type": SearchType.MATCH
                },
                {
                    "field": "dumb",
                    "value": "dumbf*",
                    "search_type": SearchType.WILDCARD
                }
            ],
            "sort": [
                {
                    "field": "version",
                    "sort_type": SortType.ASC,
                    "flag_list": [SortFlag.VERSION]
                },
                {
                    "field": "bob",
                    "sort_type": SortType.ASC
                }
            ]
        }
        criteria = self.parser.from_request(request_criteria)
        self.assertEqual(expected, criteria)

    def test_listing(self):
        results = []
        expected = ["dir/test"]

        for i in range(5):
            results.append(utils.get_meta(path="/test/artifact/dir/test"))

        parsed = self.portal._list_artifacts(results, 1)
        self.assertEqual(expected, parsed)
