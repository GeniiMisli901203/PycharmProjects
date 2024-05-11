LIB = ['+', '-', '*', '/', '%', '&', '|', '^', '<', '>', '=', '<<', '>>', 'if', 'for', '.', 'emit', '?', 'array', '@', '!']

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
                    # Чтение переменной из scope
                    if isinstance(arg, str):
                        value = self.scope.get(arg)
                        if value:
                            self.stack.append(value)
                        else:
                            print(f"Variable {arg} not found")
                            break
                    else:
                        self.call_stack.append(self.pc)
                        self.pc = function_address
                else:
                    print("Function not found")
                    break
            elif op_code == 3:
                self.scope[arg] = ('function', self.pc + 1)
                self.pc += 1
            elif op_code == 4:
                # Запись значения из стека в scope
                value = self.stack.pop()
                variable_name = self.stack.pop()
                self.scope[variable_name] = value
                self.pc += 1
            elif op_code == 5:
                if self.call_stack:
                    self.pc = self.call_stack.pop() + 1
                else:
                    break
            else:
                print("Unknown operation")
                break


LIB.extend(['+', '.', 'emit', 'to'])

bytecode = [
    31, 256, 129, 5, 8, 4, 16, 12, 24, 20, 2, 121, 26, 10, 121, 26, 18, 121, 26, 5,
    32, 4, 40, 12, 34, 2, 121, 26, 10, 121, 26, 5, 0, 27, 48, 4, 24, 35, 152, 43,
    42, 2, 121, 26, 5
]

vm = VM(bytecode)
vm.run()
