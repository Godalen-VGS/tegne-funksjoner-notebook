import oppgave
import pytest

@pytest.mark.parametrize("x,forventet", [(-5, 23), (-1, 7), (0, 3), (3, -9)])
def test_f(x, forventet):
    assert oppgave.f(x) == forventet

@pytest.mark.parametrize("x,forventet", [(-5, -11), (-2, 4), (0, 4), (1, 1), (3, -11)])
def test_g(x, forventet):
    assert oppgave.g(x) == forventet
