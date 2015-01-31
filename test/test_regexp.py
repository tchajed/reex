__author__ = 'tchajed'

import unittest
from regexp import *


class RegexpParserTestCase(unittest.TestCase):
    def parse(self, s):
        return RegexParser(s).regex()

    def test_input_stream(self):
        p = RegexParser("foo")
        self.assertEquals(p.peek(), "f")
        self.assertEquals(p.peek(), "f")
        self.assertEquals(p.next(), "f")
        self.assertEquals(p.peek(), "o")
        self.assertEquals(p.next(), "o")
        p.eat("o")
        self.assertIsNone(p.peek())

    def test_single_char(self):
        r = self.parse("a")
        self.assertEqual(r, Char("a"))

    def test_choice(self):
        r = self.parse("(ab)|c")
        self.assertEqual(r, Choice(Sequence(Char("a"), Char("b")),
                                   Char("c")))

    def test_escape(self):
        r = self.parse("""a\)c|\|""")
        self.assertEqual(r, Choice(
            Sequence(Char("a"),
                     Char(")"),
                     Char("c")),
            Char("|")))

    def test_kleene(self):
        r = self.parse("a*(b|c)*df*")
        self.assertEqual(r, Sequence(
            Kleene(Char("a")),
            Kleene(Choice(Char("b"), Char("c"))),
            Char("d"),
            Kleene(Char("f")),
        ))

    def test_nonzero_repeat(self):
        r = self.parse("""(b|c)+\d*\++""")
        self.assertEqual(r, Sequence(
            Sequence(Choice(Char("b"), Char("c")),
                     Kleene(Choice(Char("b"), Char("c")))),
            Kleene(Char("d")),
            Sequence(Char("+"), Kleene(Char("+"))),
        ))


if __name__ == '__main__':
    unittest.main()
