from copy import copy

from src.pydynamo_wrapper.helpers.item_parser import ItemParser

from src.pydynamo_wrapper.helpers.attributes_to_dynamo_put import AttributesToDynamoPut
from src.pydynamo_wrapper.helpers.sk_finder import SKFinder


class DynamoObject:
    _client = None

    table_name = None

    attributes = None

    pk = None
    sk_meta = None

    def __init__(self, **attributes):
        # Process incoming arguments to set values
        self._hydrate_attribute_values(attributes)
        self.sk_meta = SKFinder(self.attributes)

    def _hydrate_attribute_values(self, attributes):
        for attribute, value in attributes.items():
            self.attributes[attribute]['value'] = value

    def save(self):
        self.instance().put_item(
            TableName=self.table_name,
            Item=self._get_base_pk_sk() | AttributesToDynamoPut(self.attributes).get_as_dynamo()
        )

    def _get_base_pk_sk(self):
        return {
            'pk': {'S': self.pk},
            'sk': {'S': self.sk_meta.attribute_value}
        }

    def delete(self):
        self.instance().delete_item(
            TableName=self.table_name,
            Key=self._get_base_pk_sk()
        )

    @classmethod
    def generate_create_table_kwargs(cls, billing_mode='PAY_PER_REQUEST'):
        return {
            'TableName': cls.table_name,
            'BillingMode': billing_mode,
            'AttributeDefinitions': [
                {
                    'AttributeName': 'pk',
                    'AttributeType': 'S',
                },
                {
                    'AttributeName': 'sk',
                    'AttributeType': 'S',
                }
            ] + [
                {
                    'AttributeName': pk_or_sk,
                    'AttributeType': meta['type']
                }
                for attribute, meta in cls.attributes.items()
                if 'gsi' in meta
                for pk_or_sk in [f'by_{attribute}', f'by_{attribute}_by_{meta["gsi"]["sk"]}']
            ],
            'KeySchema': [
                {
                    'AttributeName': 'pk',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'sk',
                    'KeyType': 'RANGE'
                }
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': f'{attribute}',
                    'KeySchema': [
                        {
                            'AttributeName': f'by_{attribute}',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': f'by_{attribute}_by_{meta["gsi"]["sk"]}',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
                for attribute, meta in cls.attributes.items()
                if 'gsi' in meta
            ]
        }
        print('boog')

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

        return cls.create_from_attributes(
            **ItemParser(cls.attributes).parse_item_dict(response['Item'])
        )

    @classmethod
    def find_by_gsi(cls, pk, value, sk=None):
        if pk not in cls.attributes:
            raise RuntimeError(f'key \'{pk}\' doesn\'t exist on class {cls.__name__}')

        response = cls.instance().query(
            TableName=cls.table_name,
            IndexName=pk,
            KeyConditionExpression=f'by_{pk} = :value',
            ExpressionAttributeValues={
                ':value': {'S': f'{pk}/{value}'},
            }
        )['Items']


        print('s')
        return [
            cls.create_from_attributes(**ItemParser(cls.attributes).parse_item_dict(item_dict))
            for item_dict in response
        ]

    @classmethod
    def instance(cls):
        if 'boto3' not in globals():
            import boto3

        if not cls._client:
            cls._client = boto3.client('dynamodb')

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
        return f'<{self.__class__.__name__}: {self.pk}/{self.sk_meta.attribute_value}>'
