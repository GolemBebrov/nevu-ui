import pytest

from nevu_ui.fast.nvvector2 import NvVector2
from nevu_ui.utils.convertor import Convertor

# --- Tests for Convertor.to_int ---

@pytest.mark.parametrize("input_item, expected_output", [
    (10, 10),
    (10.7, 10),
    (NvVector2(3, 4), 5),
])
def test_to_int_valid_inputs(input_item, expected_output):
    result = Convertor.to_int(input_item)
    assert isinstance(result, int)
    assert result == expected_output

def test_to_int_invalid_input_raises_error():
    with pytest.raises(ValueError):
        Convertor.to_int("not_an_int")

# --- Tests for Convertor.to_float ---

@pytest.mark.parametrize("input_item, expected_output", [
    (10.5, 10.5),
    (10, 10.0),
    (NvVector2(3, 4), 5.0),
])
def test_to_float_valid_inputs(input_item, expected_output):
    result = Convertor.to_float(input_item)
    assert isinstance(result, float)
    assert result == expected_output

def test_to_float_invalid_input_raises_error():
    with pytest.raises(ValueError):
        Convertor.to_float([1, 2, 3])

# --- Tests for Convertor._to_vector2 ---

@pytest.mark.parametrize("input_item", [
    (10, 20),
    [10, 20],
    NvVector2(10, 20)
])
def test_to_vector2_valid_inputs(input_item):
    result = Convertor._to_vector2(input_item)
    assert isinstance(result, NvVector2)
    assert result.x == 10
    assert result.y == 20

@pytest.mark.parametrize("invalid_input", [
    "not_a_vector",
    (1, 2, 3),
    123
])
def test_to_vector2_invalid_input_raises_error(invalid_input):
    with pytest.raises(ValueError):
        Convertor._to_vector2(invalid_input)

# --- Tests for Convertor._to_iterable ---

@pytest.mark.parametrize("input_item, needed_type, expected_output", [
    ([1, 2], tuple, (1, 2)),
    ((1, 2), list, [1, 2]),
    ([1, 2], list, [1, 2]),
])
def test_to_iterable_valid_inputs(input_item, needed_type, expected_output):
    result = Convertor._to_iterable(input_item, needed_type)
    assert isinstance(result, needed_type)
    assert result == expected_output

def test_to_iterable_invalid_input_raises_error():
    with pytest.raises(ValueError):
        Convertor._to_iterable(123, list)

# --- Tests for Convertor.convert (dispatcher) ---

@pytest.mark.parametrize("item, to_type, expected_value", [
    ((1, 2), NvVector2, NvVector2(1, 2)),
    ([3, 4], tuple, (3, 4)),
    ((5, 6), list, [5, 6]),
    (7.8, int, 7),
    (9, float, 9.0),
    ("hello", str, "hello"),
])
def test_convert_dispatcher(item, to_type, expected_value):
    result = Convertor.convert(item, to_type)
    assert result == expected_value
    if not isinstance(expected_value, str):
        assert isinstance(result, to_type)