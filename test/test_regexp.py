__author__ = 'tchajed'

import unittest
from regexp import *


def parse(s):
    return RegexParser(s).regex()


class RegexpParserTestCase(unittest.TestCase):
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
        r = parse("a")
        self.assertEqual(r, Char("a"))

    def test_choice(self):
        r = parse("(ab)|c")
        self.assertEqual(r, Choice(Sequence(Char("a"), Char("b")),
                                   Char("c")))

    def test_escape(self):
        r = parse("""a\)c|\|""")
        self.assertEqual(r, Choice(
            Sequence(Char("a"),
                     Char(")"),
                     Char("c")),
            Char("|")))

    def test_repeat(self):
        r = parse("a*(b|c)*df*")
        self.assertEqual(r, Sequence(
            Repeat(Char("a")),
            Repeat(Choice(Char("b"), Char("c"))),
            Char("d"),
            Repeat(Char("f")),
        ))

    def test_nonzero_repeat(self):
        r = parse("""(b|c)+\d*\++""")
        self.assertEqual(r, Sequence(
            Sequence(Choice(Char("b"), Char("c")),
                     Repeat(Choice(Char("b"), Char("c")))),
            Repeat(Char("d")),
            Sequence(Char("+"), Repeat(Char("+"))),
        ))


class RegexMatchesEmptyTestCase(unittest.TestCase):
    def test_empty(self):
        r = parse("")
        self.assertTrue(r.matches_empty())

    def test_null(self):
        r = Null()
        self.assertFalse(r.matches_empty())

    def test_choice(self):
        r = parse("(a|b|)")
        self.assertTrue(r.matches_empty())
        r = parse("a|b|f*")
        self.assertTrue(r.matches_empty())
        r = parse("(a|b|c+)|(abc)")
        self.assertFalse(r.matches_empty())

    def test_repeat(self):
        r = parse("(abc|de)*")
        self.assertTrue(r.matches_empty())
        r = parse("(abc|de)+")
        self.assertFalse(r.matches_empty())

    def test_sequence(self):
        r = parse("(ab)*cd")
        self.assertFalse(r.matches_empty())
        r = parse("(ab)*(c|d|)")
        self.assertTrue(r.matches_empty())
        r = Sequence()
        self.assertTrue(r.matches_empty())


if __name__ == '__main__':
    unittest.main()
