
class AttributesToDynamoPut:
    def __init__(self, attributes):
        self.attributes = attributes

    def get_as_dynamo(self):
        attributes = {}
        for attribute, meta in self.attributes.items():
            if 'mapped_type' not in meta:
                attributes.update(self._add_non_mapped_attrs(attribute, meta))
            else:
                if 'value' not in meta:
                    continue
                attributes.update(self._add_mapped_attrs(attribute, meta))

        return attributes

    @staticmethod
    def _add_mapped_attrs(attribute, meta):
        attributes = {}
        for key, value in meta['value'].items():
            attributes[f'mapped/{attribute}/{key}'] = {
                meta['mapped_type']: str(value)
            }

        return attributes

    def _add_non_mapped_attrs(self, attribute, meta):
        attributes = {}
        if 'gsi' in meta:
            kv_attrs = {
                attribute: meta['value'] for attribute, meta in self.attributes.items() if 'value' in meta
            }
            attributes[f'by_{attribute}'] = {
                'S': f'{attribute}/{{{attribute}}}'.format(**kv_attrs)
            }
            attributes[f'by_{attribute}_by_{meta["gsi"]["sk"]}'] = {
                'S': f'{attribute}/{{{attribute}}}/{meta["gsi"]["sk"]}/{{{meta["gsi"]["sk"]}}}'.format(**kv_attrs)
            }
        else:
            attributes[attribute] = {meta['type']: meta['value']}

        return attributes
