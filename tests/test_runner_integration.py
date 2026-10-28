import pytest

from scripts.local_smoke import run_smoke


@pytest.mark.parametrize("provider", ["brave", "serper"])
@pytest.mark.parametrize("failures", [False, True])
def test_production_cli_with_mock_http_transport(provider, failures):
    result = run_smoke(provider, failures)
    assert result["first_run"]["accepted"] == 2
    assert result["repeat_run"]["judged"] == 0
