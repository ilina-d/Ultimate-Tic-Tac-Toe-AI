import pytest


class TestRunner:
    """ Class for running various/all tests. """

    def test_utils(self):
        pytest.main(['unit/', '-v'])