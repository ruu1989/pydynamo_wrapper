import os

import boto3

from moto import mock_dynamodb
from unittest import TestCase

from src.pydynamo_wrapper.base import DynamoObject


class Person(DynamoObject):
    table_name = 'my_table'
    pk = 'people/here'

    attributes = {
        'user_id': {'type': 'S', 'sk': True},
        'location': {
            'type': 'S',
            'gsi': {
                'sk': 'role'
            }
        },
        'role': {
            'type': 'S',
            'gsi': {
                'sk': 'location'
            }
        },
        'favourite_colours': {
            'mapped_type': 'S'
        }
    }


class E2ETestCase(TestCase):
    dynamodb_client = None
    dynamodb = None

    @classmethod
    def setUpClass(cls):
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'

        cls.dynamodb = mock_dynamodb()
        cls.dynamodb.start()

    def setUp(self):
        self.dynamodb_client = boto3.client('dynamodb', region_name='eu-west-2')
        self.dynamodb_client.create_table(
            **Person.generate_create_table_kwargs()
        )

    def tearDown(self):
        self.dynamodb_client.delete_table(
            TableName=Person.table_name
        )

    @classmethod
    def tearDownClass(cls):
        cls.dynamodb.stop()

    def test_create_and_find_person_from_attributes(self):
        Person.create_from_attributes(
            user_id='1234',
            location='somewhere',
            role='code_monkey',
            favourite_colours={
                'red': 'f00',
                'green': '0f0',
            }
        ).save()

        person = Person.find_by_sk('1234')

        self.assertEqual('1234', person.user_id)
        self.assertDictEqual(
            {
                'red': 'f00',
                'green': '0f0',
            },
            person.favourite_colours
        )

    def test_find_person_by_location(self):
        Person.create_from_attributes(user_id='1', location='somewhere', role='code_monkey').save()
        Person.create_from_attributes(user_id='2', location='else', role='code_monkey').save()
        Person.create_from_attributes(user_id='3', location='else', role='code_monkey').save()

        matches = Person.find_by_gsi('location', 'somewhere')
        self.assertEqual(1, len(matches))
        self.assertListEqual(['1'], [m.user_id for m in matches])

        matches = Person.find_by_gsi('location', 'else')
        self.assertEqual(2, len(matches))
        self.assertListEqual(['2', '3'], [m.user_id for m in matches])
