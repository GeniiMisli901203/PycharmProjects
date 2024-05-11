class MealyError(Exception):
    pass


class StateMachine:
    def __init__(self):
        self.state = "A"

    def crack(self):
        if self.state == "A":
            self.state = "B"
            return 0
        if self.state == "C":
            self.state = "F"
            return 5

    def coat(self):
        if self.state == "B":
            self.state = "C"
            return 2
        if self.state == "C":
            self.state = "D"
            return 4
        if self.state == "E":
            self.state = "F"
            return 8
        if self.state == "D":
            self.state = "E"
            return 7

    def peep(self):
        if self.state == "B":
            self.state = "F"
            return 3
        if self.state == "C":
            self.state = "E"
            return 6
        if self.state == "A":
            self.state = "D"
            return 1
        if self.state == "F":
            self.state = "G"
            return 9


def main():
    return StateMachine()


def raises(func, error):
    output = None
    try:
        output = func()
    except Exception as e:
        assert type(e) == error
    assert output is None


def test():
    # 1
    o = main()
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 3
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 9
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)

    # 2
    o = main()
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 2
    assert o.crack() == 5
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 9
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)

    # 3
    o = main()
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 2
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 6
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 8
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 9
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)

    # 4
    o = main()
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.peep(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.coat() == 2
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 4
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 7
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 8
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 9
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)

    # 5
    o = main()
    raises(lambda: o.coat(), MealyError)
    assert o.peep() == 1
    raises(lambda: o.peep(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.coat() == 7
    raises(lambda: o.peep(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.coat() == 8
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 9
    raises(lambda: o.coat(), MealyError)
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)


if __name__ == "__main__":
    test()
