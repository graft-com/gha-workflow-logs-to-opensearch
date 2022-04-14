# builtins
import logging
import os
import datetime
import sys

# third party
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3

SEARCH_HOST = os.environ.get("INPUT_SEARCH_HOST")
SEARCH_INDEX = os.environ.get("INPUT_SEARCH_INDEX")
SEARCH_REGION = os.environ.get("INPUT_SEARCH_REGION")

try:
    assert SEARCH_HOST not in (None, '')
except:
    output = "The input SEARCH_HOST is not set"
    print(f"Error: {output}")
    sys.exit(-1)

try:
    assert SEARCH_INDEX not in (None, '')
    now = datetime.datetime.now()
    search_index = f"{SEARCH_INDEX}-{now.month}-{now.day}"
except:
    output = "The input SEARCH_INDEX is not set"
    print(f"Error: {output}")
    sys.exit(-1)

try:
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, SEARCH_REGION)
    index_name = "gha"

    search = OpenSearch(
        hosts = [{'host': SEARCH_HOST, 'port': 443}],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
except Exception as exc:
    output = "Authentication to OpenSearch failed"
    print(f"Error: {output}")
    sys.exit(-1)


class SearchHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super(SearchHandler, self).__init__(*args, **kwargs)
        self.buffer = []

    def emit(self, record):
        try:
            record_dict = record.__dict__
            record_dict["@timestamp"] = int(record_dict.pop("created") * 1000)
            self.buffer.append({
                "_index": search_index,
                **record_dict
            })
        except ValueError as e:
            output = f"Error inserting to OpenSearch {str(e)}"
            print(f"Error: {output}")
            print(f"::set-output name=result::{output}")
            return

    def flush(self):
        # if the index is not exist, create it with mapping:
        if not search.indices.exists(index=search_index):
            mapping = '''
            {  
              "mappings":{  
                  "properties": {
                    "@timestamp": {
                      "type":   "date",
                      "format": "epoch_millis"
                    }
                  }
                }
            }'''
            es.indices.create(index=search_index, body=mapping)
        # commit the logs to opensearch
        bulk(
            client=search,
            actions=self.buffer
        )
