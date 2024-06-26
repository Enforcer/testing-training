import pytest
from _pytest.fixtures import SubRequest


class TestMathFunctions:

    @pytest.mark.parametrize("string", ["hello", "world", "pytest"])
    def test_reverse_string(self, string) -> None:
        assert string == string[::-1][::-1]


@pytest.fixture(autouse=True)
def second_implementation(request: SubRequest) -> None:
    """Look here after implementing it in pytest_collection_modifyitems."""
    pass
