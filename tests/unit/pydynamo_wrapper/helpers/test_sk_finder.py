from unittest import TestCase

from src.pydynamo_wrapper.exceptions import NoSKFoundException, MultipleSKsFoundException
from src.pydynamo_wrapper.helpers.sk_finder import SKFinder


class SKFinderTestCase(TestCase):
    def test_happy_path(self):
        finder = SKFinder(
            {
                'name': {'type': 'S', 'sk': True, 'value': 'some_person'}
            }
        )

        self.assertEqual('name', finder.attribute_name)
        self.assertEqual('some_person', finder.attribute_value)
        self.assertEqual('S', finder.attribute_type)

    def test_throws_exception_if_no_sk(self):
        with self.assertRaises(NoSKFoundException):
            SKFinder({})

    def test_throws_exception_if_multiple_sk(self):
        with self.assertRaises(MultipleSKsFoundException):
            SKFinder(
                {
                    'name': {'type': 'S', 'sk': True},
                    'another': {'type': 'S', 'sk': True},
                }
            )
