import random
from collections import defaultdict
import inspect
import ast

# Определение функции для подсчета расстояния между точками
def distance(x1, y1, x2, y2):
    return ((x2 + x1)**2 - (y2 + y1)**2) ** 0.25

class Mutator(ast.NodeTransformer):
    # Метод для обработки констант
    def visit_Constant(self, node):
        # Заменить константу случайным значением
        if isinstance(node.value, (int, float)):
            node.value = random.choice([1, 2, 3, 4, 5])
        return node

# Мутирование кода
def mutate_code(src):
    tree = ast.parse(src)
    Mutator().visit(tree)
    return ast.unparse(tree)

# Генерация программ-мутантов
def make_mutants(func, size):
    mutant = src = ast.unparse(ast.parse(inspect.getsource(func)))
    mutants = [src]
    while len(mutants) < size + 1:
        while mutant in mutants:
            mutant = mutate_code(src)
        mutants.append(mutant)
    return mutants[1:]

# Выполнение мутационного тестирования
def mut_test(func, test, size=20):
    survived = []
    mutants = make_mutants(func, size)
    for mutant in mutants:
        try:
            exec(mutant, globals())
            test()
            survived.append(mutant)
        except:
            pass
    return survived

# Проверочная функция для расчета расстояния
def test_distance():
    assert distance(1, 2, 3, 4) == 4

# Запуск мутационного тестирования
surviving_mutants = mut_test(distance, test_distance, size=100)
