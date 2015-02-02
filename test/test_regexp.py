__author__ = 'tchajed'

import unittest
from regexp import *


def parse(s):
    return RegexParser(s).regex()


def match(re, s):
    return parse(re).match(s)


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
            Choice(Char("b"), Char("c")), Repeat(Choice(Char("b"), Char("c"))),
            Repeat(Char("d")),
            Char("+"), Repeat(Char("+")),
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


class RegexMatchingTestCase(unittest.TestCase):
    def test_derivative(self):
        self.assertEqual(parse("abc").derivative("a").simplify(), parse("bc"))
        self.assertEqual(parse("a").derivative("c"), Null())
        self.assertEqual(parse("a").derivative("a"), Empty())
        self.assertEqual(Empty().derivative("c"), Null())
        self.assertEqual(Null().derivative("c"), Null())

    def test_simple_strings(self):
        self.assertTrue(match("abc", "abc"))
        self.assertFalse(match("abc", "ab"))
        self.assertFalse(match("ab", "abc"))

    def test_choice(self):
        re = "(ab|c)(d|ef)(g|h+)"
        # matching cases
        self.assertTrue(match(re, "abdg"))
        self.assertTrue(match(re, "abefg"))
        self.assertTrue(match(re, "abefhhhh"))
        self.assertTrue(match(re, "abdg"))
        # non-matching cases
        self.assertFalse(match(re, "abdefg"))  # both from 2nd group
        self.assertFalse(match(re, "abef"))  # missing last group
        self.assertFalse(match(re, "aefg"))  # missing b from "ab"
        self.assertFalse(match(re, ""))

    def test_repeat(self):
        re = "(ab)*(ce)*"
        # matching cases
        self.assertTrue(match(re, "ababce"))
        self.assertTrue(match(re, "abababcececece"))
        self.assertTrue(match(re, "abab"))
        self.assertTrue(match(re, "ab"))
        self.assertTrue(match(re, "cece"))
        self.assertTrue(match(re, "ce"))
        self.assertTrue(match(re, ""))
        # non-matching cases
        self.assertFalse(match(re, "ababc"))
        self.assertFalse(match(re, "c"))
        self.assertFalse(match(re, "abace"))

    def test_empty(self):
        self.assertTrue(Empty().match(""))
        self.assertFalse(Empty().match("a"))
        self.assertFalse(Empty().match("abc"))

    def test_null(self):
        self.assertFalse(Null().match(""))
        self.assertFalse(Null().match("a"))
        self.assertFalse(Null().match("abc"))


class RegexGenerationTestCase(unittest.TestCase):
    def test_next_chars(self):
        cases = [
            ("(ab)*(ce)*", set("ac")),
            ("abc", set("a")),
            ("(ab|c*)|(d+)", set("acd")),
            ("(a|b|c|d|(ef))+h", set("abcde")),
        ]
        for reStr, expected in cases:
            re = parse(reStr)
            with self.subTest(re=reStr):
                self.assertSetEqual(re.next_chars(), expected)

    def random_match(self, re, **kwargs):
        """ Helper that calls random_match and verifies the re matches the resulting string.

        """
        s = re.random_match(**kwargs)
        self.assertTrue(re.match(s))
        return s

    def test_random_match(self):
        cases = [
            "(ab)*(ce)*",
            "(a|b)+cd(a|b)+",
            "(a*bcd(123)+)|(hij*abc)+",
            "a|(b*)",
        ]
        ITERS = 20
        for reStr in cases:
            re = parse(reStr)
            with self.subTest(re=reStr):
                with self.subTest(stop_method="stop_p"):
                    for _ in range(ITERS):
                        self.random_match(re, stop_p=0.10, length=None)
                with self.subTest(stop_method="length=0"):
                    s = self.random_match(re, stop_p=0.0, length=0)
                    if re.matches_empty():
                        self.assertEqual(s, "")
                with self.subTest(stop_method="length"):
                    for _ in range(ITERS):
                        self.random_match(re, stop_p=0.0, length=5)
                        self.random_match(re, stop_p=0.0, length=10)
                with self.subTest(stop_method="stop_p+length"):
                    for _ in range(ITERS):
                        self.random_match(re, stop_p=0.10, length=5)
                        self.random_match(re, stop_p=0.10, length=10)


if __name__ == '__main__':
    unittest.main()
