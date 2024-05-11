LIB = [
    '+', '-', '*', '/', '%', '&', '|', '^', '<', '>', '=', '<<', '>>', 'if',
    'for', '.', 'emit', '?', 'array', '@', '!'
]


class VM:
    def __init__(self, code):
        self.stack = []
        self.code = code
        self.pc = 0
        self.scope = {}
        self.call_stack = []

    def run(self):
        while self.pc < len(self.code):
            instruction = self.code[self.pc]
            op_code = instruction & 0b111
            arg = instruction >> 3

            if op_code == 0:
                self.stack.append(arg)
                self.pc += 1
            elif op_code == 1:
                if arg < len(LIB):
                    operation = LIB[arg]
                    if operation == '+':
                        a = self.stack.pop()
                        b = self.stack.pop()
                        self.stack.append(a + b)
                    elif operation == '.':
                        print(self.stack.pop())
                    elif operation == 'emit':
                        print(chr(self.stack.pop()), end='')
                self.pc += 1
            elif op_code == 2:
                function_address = self.scope.get(arg, (0, 0))[1]
                if function_address:
                    self.call_stack.append(self.pc)
                    self.pc = function_address
                else:
                    print("Function not found")
                    break
            elif op_code == 3:
                self.scope[arg] = ('function', self.pc + 1)
                self.pc += 1
            elif op_code == 5:
                if self.call_stack:
                    self.pc = self.call_stack.pop() + 1
                else:
                    break
            else:
                print("Unknown operation")
                break


LIB.extend(['+', '.', 'emit'])

# Тестирование на предоставленном байткоде
bytecode = [
    57, 8440, 129, 8704, 129, 8688, 129, 8600, 129, 8704, 129, 8576, 129, 8672,
    129, 8672, 129, 8576, 129, 256, 129, 8728, 129, 8712, 129, 8696, 129, 8616,
    129, 8768, 129, 8680, 129, 8688, 129, 256, 129, 8592, 129, 8792, 129, 8696,
    129, 8688, 129, 8664, 129, 8680, 129, 8616, 129, 8680, 129, 8576, 129, 264,
    129, 5, 0, 3, 2, 5
]
vm = VM(bytecode)
vm.run()
