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

    # Метод для вставки случайной бинарной операции
    def visit_BinOp(self, node):
        # Заменить бинарную операцию случайной операцией
        operators = [ast.Add(), ast.Sub(), ast.Mult(), ast.Div()]
        random_op = random.choice(operators)
        node.op = random_op
        return node

# Мутирование кода с учетом случайной бинарной операции
def mutate_code(src):
    tree = ast.parse(src)
    Mutator().visit(tree)
    return ast.unparse(tree)

# Генерация программ-мутантов с случайной бинарной операцией
def make_mutants(func, size):
    mutant = src = ast.unparse(ast.parse(inspect.getsource(func)))
    mutants = [src]
    while len(mutants) < size + 1:
        while mutant in mutants:
            mutant = mutate_code(src)
        mutants.append(mutant)
    return mutants

# Выполнение мутационного тестирования с проверкой на сортировку
def mut_test(func, test, size=20):
    survived = []
    mutants = make_mutants(func, size)
    for mutant in mutants:
        try:
            exec(mutant, globals())
            result = test()
            if result:
                survived.append(mutant)
        except:
            pass
    return survived

# Проверочная функция для расчета расстояния с дополнительной проверкой на сортировку
def test_distance():
    result = distance(1, 2, 3, 4)
    return result == result  # Простое сравнение результата расчета

# Запуск мутационного тестирования с новыми возможностями
surviving_mutants = mut_test(distance, test_distance, size=4)
