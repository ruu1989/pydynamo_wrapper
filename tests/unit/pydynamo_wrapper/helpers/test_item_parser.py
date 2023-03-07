from unittest import TestCase

from src.pydynamo_wrapper.helpers.item_parser import ItemParser


class ItemParserTestCase(TestCase):
    attributes = {
        'name': {'type': 'S'},
        'colours': {
            'mapped_type': 'S'
        },
        'numbers': {
            'mapped_type': 'N'
        }
    }

    item_parser = ItemParser(attributes)

    def test_parse_scalar_attributes(self):
        scalar_attributes = self.item_parser._get_scalar_attributes(
            {
                'name': {'S': 'some name'}
            }
        )

        self.assertDictEqual(
            {'name': 'some name'},
            scalar_attributes
        )

    def test_parse_mapped_attributes_simple_case(self):
        mapped_attributes = self.item_parser._get_mapped_attributes(
            {
                'mapped/colours/red': {'S': 'ff0000'},
                'mapped/colours/blue': {'S': '0000ff'}
            }
        )

        self.assertDictEqual(
            {'colours': {'red': 'ff0000', 'blue': '0000ff'}},
            mapped_attributes
        )

    def test_parse_mapped_attributes_handles_names_with_slashes(self):
        mapped_attributes = self.item_parser._get_mapped_attributes(
            {
                'mapped/colours/red/orange': {'S': 'ff5349'}
            }
        )

        self.assertDictEqual(
            {'colours': {'red/orange': 'ff5349'}},
            mapped_attributes
        )

    def test_undefined_attributes_do_not_get_added_to_response(self):
        parsed = self.item_parser.parse_item_dict(
            {
                'some other attribute': {'S', 'blah'}
            }
        )

        self.assertDictEqual(
            {},
            parsed
        )

    def test_type_handling_for_numbers(self):
        mapped_attributes = self.item_parser._get_mapped_attributes(
            {
                'mapped/numbers/six_point_five': {'N': '6.5'}
            }
        )

        self.assertDictEqual(
            {'numbers': {'six_point_five': 6.5}},
            mapped_attributes
        )
