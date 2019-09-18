import sys
sys.path.insert(0, '/opt')
import boto3
from ask_sdk_dynamodb.adapter import DynamoDbAdapter, user_id_partition_keygen
import os


region_name = os.getenv("AWS_REGION", "us-east-1")
dynamodb = boto3.resource('dynamodb', region_name=region_name)
adaptor = DynamoDbAdapter(table_name="sumoalexa",
                                partition_key_name="user_id",  # the ID you choose while creating the table
                                partition_keygen=user_id_partition_keygen,  # default
                                create_table=True,  # default
                                dynamodb_resource=dynamodb)
class KVStore(object):

    def __init__(self, req_env, adaptor):
        # req_env is handler_input.request_envelope
        self.request_envelope = req_env
        self.kvstore = adaptor

    def save(self, obj):
        self.kvstore.save_attributes(request_envelope=self.request_envelope, attributes=obj)

    def get(self):
        return self.kvstore.get_attributes(request_envelope=self.request_envelope)

