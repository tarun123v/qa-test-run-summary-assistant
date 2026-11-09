import pytest

from qa_tools import get_test_run


def test_get_test_run_raises_documented_error_for_empty_id():
    with pytest.raises(ValueError) as error:
        get_test_run("")

    assert str(error.value) == "run_id must not be empty."

