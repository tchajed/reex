__author__ = 'tchajed'


class Regex:
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def matches_empty(self):
        """ Returns True if the regex can match the empty string.

        :rtype: bool
        """
        return True

    def derivative(self, c):
        """
        Take the derivative of self with respect to c.

        The derivative is a new regex that matches what self would match
        after it had already matched c. If self cannot match c, the new regex
        will be equivalent to Null().

        :param c: the next character to match
        :return: the derivative regex
        :rtype: Regex
        """
        return Null()

    def match(self, s):
        regex = self
        for ch in s:
            regex = regex.derivative(ch)
        return regex.matches_empty()


class Empty(Regex):
    """ Match only the empty string. """

    def __str__(self):
        return ""

    def __repr__(self):
        return "Empty()"


class Null(Regex):
    """ Match nothing. """

    def matches_empty(self):
        return False

    def __str__(self):
        # There's really no regex syntax to express this idea.
        return "#null#"

    def __repr__(self):
        return "Null()"


class Char(Regex):
    """ Match a single character. """

    def __init__(self, char):
        self.char = char

    def matches_empty(self):
        return False

    def derivative(self, c):
        if self.char == c:
            return Empty()
        return Null()

    def __str__(self):
        return self.char

    def __repr__(self):
        inner = self.char
        if inner in ["(", ")"]:
            inner = "\\" + inner
        return "Char({})".format(inner)


class Choice(Regex):
    """ Match either of two regexes. """

    def __init__(self, left, right):
        """
        :type left: Regex
        :type right: Regex
        """
        self.left = left
        self.right = right

    def matches_empty(self):
        return self.left.matches_empty() or self.right.matches_empty()

    def derivative(self, c):
        return Choice(self.left.derivative(c),
                      self.right.derivative(c))

    def __str__(self):
        return str(self.left) + "|" + str(self.right)

    def __repr__(self):
        return "Choice({}, {})".format(repr(self.left),
                                       repr(self.right))


class Sequence(Regex):
    """ A sequence of regexes. """

    def __init__(self, *elements):
        """
        :type elements: list[Regex]
        """
        self.elements = list(elements)

    def head(self):
        if not self.elements:
            return Empty()
        return self.elements[0]

    def tail(self):
        if not self.elements or len(self.elements) == 1:
            return Empty()
        return Sequence(*self.elements[1:]).simplify()

    def derivative(self, c):
        head = self.head()
        tail = self.tail()
        head_derivative = Sequence(head.derivative(c), tail).simplify()
        if head.matches_empty():
            return Choice(tail.derivative(c),  # match head against empty
                          head_derivative)
        return head_derivative

    def matches_empty(self):
        return all([re.matches_empty() for re in self.elements])

    def add(self, el):
        self.elements.append(el)

    def simplify(self):
        """
        Return a new regex equivalent to this regex, using a Sequence only to
        hold more than 1 element.

        :rtype: Regex
        """
        if len(self.elements) == 0:
            return Empty()
        if len(self.elements) == 1:
            return self.elements[0]
        elements = [el for el in self.elements if not isinstance(el, Empty)]
        if all([isinstance(el, Sequence) for el in elements]):
            grouped_elements = []
            for el in elements:
                grouped_elements.extend(el.elements)
            elements = grouped_elements
        return Sequence(*elements)

    def __str__(self):
        return "".join(map(str, self.elements))

    def __repr__(self):
        return "Sequence({})".format(
            ", ".join(map(repr, self.elements))
        )


class Repeat(Regex):
    """ Zero or more repetitions of a regex (Kleene star operator). """

    def __init__(self, regex):
        self.regex = regex

    def derivative(self, c):
        return Sequence(self.regex.derivative(c), Repeat(self.regex))

    def __str__(self):
        inner = str(self.regex)
        if isinstance(self.regex, Char):
            return inner + "*"
        return "(" + inner + ")*"


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
            return Repeat(base)
        if self.peek() == '+':
            self.eat("+")
            return Sequence(base, Repeat(base))
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
