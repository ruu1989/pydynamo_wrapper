from src.pydynamo_wrapper.exceptions import NoSKFoundException, MultipleSKsFoundException


class SKFinder:
    attribute_name = None
    attribute_value = None
    attribute_type = None

    def __init__(self, attributes):
        self.attributes = attributes
        self._parse_sk_from_attributes()

    def _parse_sk_from_attributes(self):
        attribute_name = [
            attribute_name
            for attribute_name, meta
            in self.attributes.items() if 'sk' in meta
        ]

        if not attribute_name:
            raise NoSKFoundException

        if len(attribute_name) > 1:
            raise MultipleSKsFoundException

        self.attribute_name = attribute_name[0]
        self.attribute_value = self.attributes[self.attribute_name]['value']
        self.attribute_type = self.attributes[self.attribute_name]['type']
