__author__ = 'tchajed'


class Regex:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class Choice(Regex):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.left) + "|" + str(self.right)

    def __repr__(self):
        return "Choice({}, {})".format(repr(self.left),
                                       repr(self.right))


class Empty(Regex):
    pass

    def __str__(self):
        return ""

    def __repr__(self):
        return "Empty()"


class Sequence(Regex):
    def __init__(self, *elements):
        self.elements = list(elements)

    def add(self, el):
        self.elements.append(el)

    def simplify(self):
        if len(self.elements) == 0:
            return Empty()
        if len(self.elements) == 1:
            return self.elements[0]
        return self

    def __str__(self):
        return "".join(map(str, self.elements))

    def __repr__(self):
        return "Sequence({})".format(
            ", ".join(map(repr, self.elements))
        )


class Kleene(Regex):
    def __init__(self, regex):
        self.regex = regex

    def __str__(self):
        inner = str(self.regex)
        if isinstance(self.regex, Char):
            return inner + "*"
        return "(" + inner + ")*"


class Char(Regex):
    def __init__(self, char):
        self.char = char

    def __str__(self):
        return self.char

    def __repr__(self):
        inner = self.char
        if inner in ["(", ")"]:
            inner = "\\" + inner
        return "Char({})".format(inner)


class RegexParser:
    def __init__(self, text):
        self.text = text

    def peek(self):
        if len(self.text) == 0:
            return None
        return self.text[0]

    def next(self):
        n = self.text[0]
        self.text = self.text[1:]
        return n

    def eat(self, item):
        n = self.next()
        if n != item:
            raise ValueError("Expected {} but got {}".format(item, n))

    # TODO: add groups

    def regex(self):
        term = self.term()
        if self.peek() == '|':
            self.eat("|")
            regex = self.regex()
            return Choice(term, regex)
        return term

    def term(self):
        factors = Sequence()
        while (self.peek() is not None and
                self.peek() != ')' and self.peek() != '|'):
            factor = self.factor()
            factors.add(factor)
        return factors.simplify()

    def factor(self):
        base = self.base()
        if self.peek() == '*':
            self.eat("*")
            return Kleene(base)
        if self.peek() == '+':
            self.eat("+")
            return Sequence(base, Kleene(base))
        return base

    def base(self):
        if self.peek() == "\\":
            self.eat("\\")
            return Char(self.next())
        if self.peek() == "(":
            self.eat("(")
            regex = self.regex()
            self.eat(")")
            return regex
        return Char(self.next())
