
class TestGroupOne:
    def test_example_1(self):
        pass

    def test_example_2(self):
        pass


class TestGroupTwo:
    def test_example_1(self):
        pass

    def test_example_2(self):
        pass

import pytest
@pytest.mark.skip(dupa=1)
class TestCommon:
    def test_example_1(self):
        pass

    def test_example_2(self):
        pass
