import random
from collections import defaultdict
import inspect
import ast

def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def classify_triangle(x1, y1, x2, y2, x3, y3):
    a = distance(x1, y1, x2, y2)
    b = distance(x2, y2, x3, y3)
    c = distance(x3, y3, x1, y1)
    if a == b == c:
        return "равносторонний"
    elif a == b or a == c or b == c:
        return "равнобедренный"
    elif a != b != c:
        return "разносторонний"

class Mutator(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, int):
            new_value = random.randint(-100, 100)  # Замените на диапазон, который вам подходит
            return ast.Constant(value=new_value)
        elif isinstance(node.value, float):
            new_value = random.uniform(-100, 100)  # Замените на диапазон, который вам подходит
            return ast.Constant(value=new_value)
        else:
            return node

def mutate_code(src):
    tree = ast.parse(src)
    Mutator().visit(tree)
    return ast.unparse(tree)

def make_mutants(func, size):
    mutant = src = ast.unparse(ast.parse(inspect.getsource(func)))
    mutants = [src]
    while len(mutants) < size + 1:
        while mutant in mutants:
            mutant = mutate_code(src)
        mutants.append(mutant)
    return mutants[1:]

def test_triangle_classification():
    assert classify_triangle(1, 1, 1, 1, 1, 1) == "равносторонний"
    assert classify_triangle(1, 1, 2, 2, 3, 1) == "равнобедренный"
    assert classify_triangle(0, 0, 1, 1, 4, 0) == "разносторонний"

def mut_test(func, test, size=2):
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

survived_mutants = mut_test(classify_triangle, test_triangle_classification, size=2)
print("Выжившие мутанты:")
for mutant in survived_mutants:
    print(mutant)
