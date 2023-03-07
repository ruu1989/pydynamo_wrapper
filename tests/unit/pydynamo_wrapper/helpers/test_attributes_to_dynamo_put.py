from unittest import TestCase

from src.pydynamo_wrapper.helpers.attributes_to_dynamo_put import AttributesToDynamoPut


class AttributesToDynamoPutTestCase(TestCase):
    def test_add_mapped_attributes(self):
        self.assertDictEqual(
            AttributesToDynamoPut({})._add_mapped_attrs(
                'colour',
                {
                    'mapped_type': 'S',
                    'value': {'red': 'f00', 'blue': '00f'}
                }
            ),
            {
                'mapped/colour/red': {'S': 'f00'},
                'mapped/colour/blue': {'S': '00f'}
            }
        )

    def test_add_non_mapped_attributes(self):
        self.assertDictEqual(
            AttributesToDynamoPut({})._add_non_mapped_attrs(
                'name',
                {
                    'type': 'S',
                    'value': 'jeff'
                }
            ),
            {
                'name': {'S': 'jeff'}
            }
        )

    def test_add_gsi(self):
        attributes = {
            'location': {
                'type': 'S',
                'value': 'edinburgh',
                'gsi': {
                    'sk': 'role'
                }
            },
            'role': {'value': 'codemonkey'}
        }

        self.assertDictEqual(
            AttributesToDynamoPut(attributes)._add_non_mapped_attrs(
                'location',
                attributes['location']
            ),
            {
                'by_location': {'S': 'location/edinburgh'},
                'by_location_by_role': {'S': 'location/edinburgh/role/codemonkey'}
            }
        )
