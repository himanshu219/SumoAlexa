import boto3
from ask_sdk_dynamodb.adapter import DynamoDbAdapter, user_id_partition_keygen
import os


class KVStore(object):

    def __init__(self, req_env):
        # req_env is handler_input.request_envelope
        self.request_envelope = req_env
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.kvstore = DynamoDbAdapter(table_name="sumoalexa",
                                partition_key_name="user_id",  # the ID you choose while creating the table
                                partition_keygen=user_id_partition_keygen,  # default
                                create_table=False,  # default
                                dynamodb_resource=self.dynamodb)

    def save(self, obj):
        self.kvstore.save_attributes(request_envelope=self.request_envelope, attributes=obj)

    def get(self):
        return self.kvstore.get_attributes(request_envelope=self.request_envelope)

