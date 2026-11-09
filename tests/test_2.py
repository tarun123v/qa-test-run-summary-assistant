import pytest

from qa_tools import get_test_run


def test_get_test_run_raises_documented_error_for_unknown_id():
    with pytest.raises(LookupError) as error:
        get_test_run("QA-999")

    assert str(error.value) == "No QA test run found for ID QA-999."
