OP_NAMES = {0: 'push', 1: 'op', 2: 'call', 3: 'is', 4: 'to', 5: 'exit'}


def not_implemented(vm):
    raise RuntimeError('Not implemented!')


LIB = {
    '+': not_implemented,
    '-': not_implemented,
    '*': not_implemented,
    '/': not_implemented,
    '%': not_implemented,
    '&': not_implemented,
    '|': not_implemented,
    '^': not_implemented,
    '<': not_implemented,
    '>': not_implemented,
    '=': not_implemented,
    '<<': not_implemented,
    '>>': not_implemented,
    'if': not_implemented,
    'for': not_implemented,
    '.': not_implemented,
    'emit': not_implemented,
    '?': not_implemented,
    'array': not_implemented,
    '@': not_implemented,
    '!': not_implemented
}


def disasm(bytecode):
    index = 0
    result = "entry:\n"

    while index < len(bytecode):
        op = bytecode[index]

        if op in OP_NAMES:
            op_name = OP_NAMES[op]
            if op_name == "push":
                value = bytecode[index + 1]
                result += f"  {op_name} {value}\n"
                index += 2
            elif op_name == "op" or op_name == "call":
                lib_op = bytecode[index + 1]
                op_key = [key for key, value in LIB.items() if value == not_implemented][lib_op]
                result += f"  {op_name} {op_key}\n"
                index += 2
            else:
                result += f"  {op_name}\n"
                index += 1
        else:
            result += f"  {OP_NAMES[5]} {op}\n"
            break

    return result

class VM:
    def __init__(self, code):
        self.stack = []
        self.code = code

    def run(self):
        pc = 0
        while True:
            if pc >= len(self.code):
                break

            op = self.code[pc]
            if op == 0:  # push
                value = self.code[pc + 1]
                self.stack.append(value)
                pc += 2
            elif op == 1:  # op
                lib_op = self.code[pc + 1]
                op_name = [key for key, value in LIB.items() if value == not_implemented][lib_op]
                LIB[op_name](self)
                pc += 2
            elif op == 5:  # exit
                break

def add(vm):
    if len(vm.stack) < 2:
        raise RuntimeError('Not enough operands on the stack for addition')
    a = vm.stack.pop()
    b = vm.stack.pop()
    result = a + b
    vm.stack.append(result)

def output(vm):
    if len(vm.stack) < 1:
        raise RuntimeError('Nothing to output')
    value = vm.stack.pop()
    print(value)

LIB = {
    '+': add,
    '.': output,
    # Другие операции остаются неизменными
}



# Пример использования
bytecode_example = [4, 8, 2, 1, 195, 32]
print(disasm(bytecode_example))
