from hypothesis import given
from hypothesis.strategies import floats
from math import sqrt


# Определение тестируемой функции distance
def distance(x, y):
    return sqrt(x ** 2 + y ** 2)


# Определение стратегии для генерации случайных чисел типа float
@given(x=floats(), y=floats())
def test_distance(x, y):
    # Вызов тестируемой функции
    result = distance(x, y)

    # Проверка условий
    assert result >= 0, "Расстояние должно быть неотрицательным"
    # Другие проверки по необходимости


# Запуск теста
test_distance()
