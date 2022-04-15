# builtins
import datetime
import logging
import os
import sys
import traceback

# third party
from opensearch_logger import OpenSearchHandler
from requests_aws4auth import AWS4Auth

import boto3

boto3.set_stream_logger(name='boto3', level=0, format_string=None)

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
    creds = boto3.Session().get_credentials()

    handler = OpenSearchHandler(
        index_name=search_index,
        hosts=[{'host': SEARCH_HOST, 'port': 443}],
        http_auth=AWS4Auth(creds.access_key, creds.secret_key, SEARCH_REGION, 'es', session_token=creds.token),
        http_compress=True,
        use_ssl=True,
    )

except Exception as exc:
    output = "Authentication to OpenSearch failed"
    print(f"Error: {output}")
    print(f"Exception: {exc}")
    exc_info = sys.exc_info()
    print(''.join(traceback.format_exception(*exc_info)))
    sys.exit(-1)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
