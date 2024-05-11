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
            elif op == 16:  # addition
                if len(self.stack) > 1:  # Check if there are at least two values on the stack
                    a = self.stack.pop()
                    b = self.stack.pop()
                    result = a + b
                    self.stack.append(result)
                else:
                    print("Error: Not enough values on the stack for addition.")
                    break
                pc += 1
            elif op == 5:  # exit
                break

bytecode = [0, 2, 0, 2, 16, 5]  # Пример байткода для "2 2 + ."
virtual_machine = VM(bytecode)
virtual_machine.run()
print(virtual_machine.stack)  # Ожидаемый результат: [0, 16, 16, 1, 121, 5]
