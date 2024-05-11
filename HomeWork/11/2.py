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
        raise MealyError("crack")

    def coat(self):
        if self.state == "B":
            self.state = "C"
            return 2
        if self.state == "C":
            self.state = "D"
            return 4
        if self.state == "D":
            self.state = "E"
            return 7
        if self.state == "E":
            self.state = "F"
            return 8

        raise MealyError("coat")

    def peep(self):
        if self.state == "A":
            self.state = "D"
            return 1
        if self.state == "C":
            self.state = "E"
            return 6
        if self.state == "B":
            self.state = "F"
            return 3
        if self.state == "F":
            self.state = "G"
            return 9

        raise MealyError("peep")


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
    # Test case 1
    o = main()
    assert o.state == "A"
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    assert o.state == "B"
    assert o.coat() == 2
    assert o.state == "C"
    assert o.coat() == 4
    raises(lambda: o.crack(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.state == "D"
    assert o.coat() == 7
    raises(lambda: o.peep(), MealyError)
    assert o.state == "E"
    assert o.coat() == 8
    raises(lambda: o.crack(), MealyError)
    assert o.state == "F"
    assert o.peep() == 9
    raises(lambda: o.crack(), MealyError)
    assert o.state == "G"

    # Test case 2
    o = main()
    assert o.state == "A"
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    assert o.state == "B"
    assert o.peep() == 3
    raises(lambda: o.crack(), MealyError)
    assert o.state == "F"
    assert o.peep() == 9
    raises(lambda: o.crack(), MealyError)
    assert o.state == "G"

    # Test case 3
    o = main()
    assert o.state == "A"
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    assert o.state == "B"
    assert o.coat() == 2
    assert o.state == "C"
    assert o.peep() == 6
    raises(lambda: o.crack(), MealyError)
    assert o.state == "E"
    assert o.coat() == 8
    raises(lambda: o.crack(), MealyError)
    assert o.state == "F"
    assert o.peep() == 9
    raises(lambda: o.crack(), MealyError)
    assert o.state == "G"


    # Test case 4
    o = main()
    assert o.state == "A"
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    assert o.state == "B"
    assert o.coat() == 2
    assert o.state == "C"
    assert o.crack() == 5
    raises(lambda: o.crack(), MealyError)
    assert o.state == "F"
    assert o.peep() == 9
    raises(lambda: o.crack(), MealyError)
    assert o.state == "G"


    # Test case 5
    o = main()
    assert o.state == "A"
    raises(lambda: o.coat(), MealyError)
    assert o.peep() == 1
    raises(lambda: o.crack(), MealyError)
    assert o.state == "D"
    raises(lambda: o.peep(), MealyError)
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 7
    assert o.state == "E"
    raises(lambda: o.peep(), MealyError)
    raises(lambda: o.crack(), MealyError)
    assert o.coat() == 8
    assert o.state == "F"
    raises(lambda: o.crack(), MealyError)
    assert o.peep() == 9
    assert o.state == "G"

    o = main()
    assert o.state == "A"
    raises(lambda: o.coat(), MealyError)
    assert o.crack() == 0
    raises(lambda: o.crack(), MealyError)
    assert o.state == "B"
    assert o.coat() == 2
    assert o.state == "C"
    assert o.coat() == 4
    raises(lambda: o.peep(), MealyError)
    assert o.state == "D"
    raises(lambda: o.peep(), MealyError)
    assert o.coat() == 7
    raises(lambda: o.crack(), MealyError)
    assert o.state == "E"
    assert o.coat() == 8
    raises(lambda: o.crack(), MealyError)
    assert o.state == "F"
    assert o.peep() == 9
    raises(lambda: o.crack(), MealyError)
    assert o.state == "G"

if __name__ == "__main__":
    test()
