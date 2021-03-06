from unittest import TestCase
from nappingcat import patterns
from nappingcat.exceptions import NappingCatUnhandled, NappingCatBadPatterns
import random

random_value = random.randint(1,100)
def test_fn(*args, **kwargs):
    return random_value

cmdpatterns = patterns.patterns('tests',
            (r'^anything', test_fn),
            (r'^something_else', patterns.include('tests.patterns_test')),
            (r'^something', 'test_fn'),
) 

class TestOfCommandPatterns(TestCase):
    def test_init_assigns_appropriately(self):
        random_map = random.randint(1,100)
        result = patterns.CommandPatterns('', random_map)
        self.assertEqual(result.path, '')
        self.assertEqual(result.map, random_map)

        results = patterns.CommandPatterns('tests.patterns_test', '')
        self.assertEqual(random.__class__, results.module.__class__)

        self.assertRaises(ImportError, patterns.CommandPatterns, 'dne', '')

    def test_match_raises_unhandled_if_no_match(self):
        test = patterns.CommandPatterns('', [])
        anything = 'random-%d' % random.randint(1,100)
        self.assertRaises(NappingCatUnhandled, test.match, anything)

    def test_delegates_to_included_patterns(self):
        random_result = random.randint(1,100)
        class TriggerCommandPatterns(patterns.CommandPatterns):
            def match(self, command):
                return random_result
        pat = patterns.CommandPatterns('', [('^hey', TriggerCommandPatterns('', []))])
        self.assertEqual(pat.match('hey'), random_result)

    def test_continues_to_next_match_if_delegate_raises_unhandled(self):
        random_result = random.randint(1,100)
        class TriggerCommandPatterns(patterns.CommandPatterns):
            def match(self, command):
                raise NappingCatUnhandled("OH no!")
        test_fn = lambda *args, **kwargs: random_result
        pat = patterns.CommandPatterns('', [('^hey', TriggerCommandPatterns('', [])), ('^hey', test_fn)])
        target, match = pat.match('hey')
        self.assertEqual(target, test_fn)
        self.assertTrue(hasattr(match, 'groupdict'))    # not a great way to test whether or not it's a regex match object...

    def test_attempts_to_grab_str_target_off_of_module(self):
        pat = patterns.CommandPatterns('tests.patterns', [
            ('^hey', 'test_fn'),
            ('^yo', 'dne'),
        ])
        target, match = pat.match('hey')
        self.assertEqual(target, test_fn)
        self.assertTrue(hasattr(match, 'groupdict'))    # not a great way to test whether or not it's a regex match object...
        self.assertRaises(AttributeError, pat.match, 'yo')

    def test_raises_nappingcat_exception_if_target_is_not_a_string_patterns_or_callable(self):
        pat = patterns.CommandPatterns('tests.patterns', [
            ('^hey', random.randint(1,100)),
        ])
        self.assertRaises(NappingCatBadPatterns, pat.match, 'hey')

    def test_two_CommandPatterns_objects_can_be_added_together(self):
        one = patterns.CommandPatterns('tests.patterns', [
            (r'^hey', 'test_fn'),
            (r'^you!', 'dne'),
        ])

        two = patterns.CommandPatterns('tests.patterns', [
            (r'^sup', 'test_fn'),
            (r'^dawn?', 'dne'),
        ])

        both = one + two

        target, match = both.match('hey')
        self.assertEqual(target, test_fn)

        target, match = both.match('sup')
        self.assertEqual(target, test_fn, "should match the second set as well")

    def test_added_CommandPatterns_still_raise_exceptions_if_they_cannot_find_the_command(self):
        one = patterns.CommandPatterns('tests.patterns', [
            (r'^hey', 'test_fn'),
            (r'^you!', 'dne'),
        ])

        two = patterns.CommandPatterns('tests.patterns', [
            (r'^sup', 'test_fn'),
            (r'^dawn?', 'dne'),
        ])

        both = one + two

        self.assertRaises(NappingCatUnhandled, both.match, "What's up?")

    def test_can_append_to_an_existing_pattern(self):
        one = patterns.CommandPatterns('tests.patterns', [
            (r'^hey', 'test_fn'),
            (r'^you!', 'dne'),
        ])

        two = patterns.CommandPatterns('tests.patterns', [
            (r'^sup', 'test_fn'),
            (r'^dawn?', 'dne'),
        ])

        one += two

        target, match = one.match('hey')
        self.assertEqual(target, test_fn)

        target, match = one.match('sup')
        self.assertEqual(target, test_fn, "should match the second set as well")

class TestOfMultipleCommandPatterns(TestCase):
    def test_is_a_subclass_of_CommandPatterns(self):
        p = patterns.MultipleCommandPatterns()
        self.assert_(isinstance(p, patterns.CommandPatterns))
