def markov(input_string, rules):
    tape = input_string
    i = 0
    stack = []

    while i < len(tape):
        matched = False
        for pattern, replacement in rules:
            if tape[i:i + len(pattern)] == pattern:
                if pattern == '(':
                    stack.append('(')
                elif pattern == ')':
                    if not stack or stack[-1] != '(':
                        return 'Error'
                    stack.pop()

                tape = tape[:i] + replacement + tape[i + len(pattern):]
                i += len(replacement)
                matched = True
                break

        if not matched:
            return 'Error'

    if stack:
        return 'Error'
    return 'E'


rules = [
    (' ', ''),  # Удаление пробелов
    ('(', '('),
    (')', ')'),
    ('+', '+'),
    ('-', '-'),
    ('*', '*'),
    ('/', '/'),
    ('0', 'E'),
    ('1', 'E'),
    ('2', 'E'),
    ('3', 'E'),
    ('4', 'E'),
    ('5', 'E'),
    ('6', 'E'),
    ('7', 'E'),
    ('8', 'E'),
    ('9', 'E'),
    ('E+', 'E'),
    ('E-', 'E'),
    ('E*', 'E'),
    ('E/', 'E'),
    ('(E', 'E'),
    ('E)', 'E'),
    ('()', 'E')
]


def check_expression(expr):
    result = markov(expr, rules)
    return result == 'E'


# Примеры использования
print(check_expression(' -12* (1 + 4) - (123 /3) '))
print(check_expression(' -12* (1 + 4+) - (123 /3) '))
print(check_expression(' (1 + 4) '))
print(check_expression(' 1 + 4 '))
print(check_expression(' 1 + 4) '))
print(check_expression(' (1 + 4 '))
print(check_expression(' (1 + ) '))
print(check_expression(' (1 + 4) * '))
print(check_expression(' (1 + 4) * 5 '))
