from pydynamo_wrapper.src.pydynamo_wrapper.helpers.item_parser import ItemParser


class DynamoObject:
    _client = None

    table_name = None

    attributes = None

    pk = None
    sk = None
    sk_type = None

    def __init__(self, **attributes):
        # Process incoming arguments to set values
        self._hydrate_attribute_values(attributes)
        self.sk = self._get_sk_value()

    def _hydrate_attribute_values(self, attributes):
        for attribute, value in attributes.items():
            self.attributes[attribute]['value'] = value

    def _get_attributes_as_kv(self):
        return {
            attribute: meta['value']
            for attribute, meta in self.attributes.items() if 'value' in meta
        }

    def save(self):
        item = self._get_base_pk_sk()

        for attribute, meta in self.attributes.items():
            if 'mapped_type' not in meta:
                item[attribute] = {meta['type']: meta['value']}
                if 'gsi' in meta:
                    for k in ['pk', 'sk']:
                        item[meta['gsi'][k]['key']] = {
                            'S': meta['gsi'][k]['value'].format(**self._get_attributes_as_kv())
                        }

            else:
                if 'value' not in meta:
                    continue

                for key, value in meta['value'].items():

                    item[f'mapped/{attribute}/{key}'] = {
                        meta['mapped_type']: str(value)
                    }

        self.instance().put_item(
            TableName=self.table_name,
            Item=item
        )

    def _get_base_pk_sk(self):
        return {
            'pk': {'S': self.pk},
            'sk': {'S': self.sk}
        }

    def delete(self):
        self.instance().delete_item(
            TableName=self.table_name,
            Key=self._get_base_pk_sk()
        )

    @classmethod
    def find_by_sk(cls, sk):
        response = cls.instance().get_item(
            TableName=cls.table_name,
            Key={
                'pk': {'S': cls.pk},
                'sk': {'S': sk}
            }
        )

        if 'Item' not in response:
            raise RuntimeError(f'instance of {cls.__name__} with SK {sk} not found')

        item_dict = response['Item']
        new_attributes = ItemParser(cls.attributes).parse_item_dict(item_dict)

        return cls.create_from_attributes(**new_attributes)

    @classmethod
    def instance(cls):
        import boto3

        if not cls._client:
            cls._client = boto3.client(
                'dynamodb',
                aws_access_key_id='dummy',
                aws_secret_access_key='dummy',
                region_name='eu-west-2',
                endpoint_url='http://localhost:8000'
            )

        return cls._client

    @classmethod
    def create_from_attributes(cls, **attributes):
        for attribute in attributes:
            if attribute not in cls.attributes:
                raise RuntimeError(f'attribute {attribute} does not exist on {cls.__name__}')

        return cls(**attributes)

    def __getattr__(self, item):
        # Always return existing, concrete attributes, safely.
        if item in dir(self):
            return getattr(self, item)

        # Now lookup to see if we have a matching attribute of our own.
        if item in self.attributes:
            return self.attributes[item]['value']

        else:
            raise ValueError(f'Class {self.__class__.__name__} has no attribute {item}')

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.pk}/{self.sk}>'
