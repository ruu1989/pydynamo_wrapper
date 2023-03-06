class ItemParser:
    def __init__(self, attributes):
        self.attributes = attributes

    def parse_item_dict(self, item_dict):
        attributes = self._get_scalar_attributes(item_dict)
        mapped_attributes = self._get_mapped_attributes(item_dict)
        return attributes | mapped_attributes

    def _get_scalar_attributes(self, item_dict):
        scalar_attributes = {
            attribute: list(value.values())[0]
            for attribute, value in item_dict.items()
            if attribute in self.attributes
        }
        return scalar_attributes

    def _get_mapped_attributes(self, item_dict):
        mapped_attributes = {}

        for item in [item for item in item_dict if item.startswith('mapped/')]:
            item_parts = item.split('/')
            attr_group = item_parts[1]
            attr_key = '/'.join(item_parts[2:])

            if attr_group not in mapped_attributes:
                mapped_attributes[attr_group] = {}

            intended_type = self.attributes[attr_group]['mapped_type']
            value = item_dict[item][intended_type]
            mapped_attributes[attr_group][attr_key] = float(value) if intended_type == 'N' else value

        return mapped_attributes
