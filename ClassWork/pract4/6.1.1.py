bytecode_example = [0, 2, 0, 2, 1, 5]

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

        if op == 0:
            value = bytecode[index + 1]
            result += f"  push {value}\n"
            index += 2
        elif op == 1:
            lib_op = bytecode[index + 1]
            op_key = [key for key, value in LIB.items() if value == not_implemented][lib_op]
            result += f"  op {op_key}\n"
            index += 2
        elif op == 5:
            result += f"  exit\n"
            break
        else:
            result += f"  {op}\n"
            index += 1

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

def output(vm):
    if len(vm.stack) < 1:
        raise RuntimeError('Nothing to output')
    value = vm.stack.pop()
    print(value)

def add(vm):
    if len(vm.stack) < 2:
        raise RuntimeError('Not enough operands on the stack for addition')
    a = vm.stack.pop()
    b = vm.stack.pop()
    result = a + b
    vm.stack.append(result)

LIB = {
    '+': add,
    '.': output,
    'x': not_implemented,
    # Другие операции остаются неизменными
}

virtual_machine = VM(bytecode_example)
virtual_machine.run()
