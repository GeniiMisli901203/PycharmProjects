def markov(input_string, rules):
    tape = input_string
    i = 0
    while i < len(tape):
        for pattern, replacement in rules:
            if tape[i:i + len(pattern)] == pattern:
                tape = tape[:i] + replacement + tape[i + len(pattern):]
                i += len(replacement)
                break
        else:
            i += 1
    return tape

rules = [
    ('|0', '0||'),
    ('1', '0|'),
    ('0', '')
]

print(markov('101', rules))