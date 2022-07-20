#!/usr/bin/python3 -W ignore

import requests
import json
import sys
sys.path.append('/root/scripts')
import os
from get_token import get_token

NOOBAA_TOKEN = os.environ.get('TOKEN', get_token())
BUCKET = os.environ.get('BUCKET', 'nsbucket01')

API = os.environ.get('ENDPOINT', 'http://node2.example.com:8080/rpc')
rsp = requests.get(API, json=dict(api='bucket_api', method='list_buckets', params={}, auth_token=NOOBAA_TOKEN))
rsp = requests.get(API, json=dict(api='bucket_api', method='read_bucket', params=dict(name=BUCKET), auth_token=NOOBAA_TOKEN))
data = rsp.json()
data = data.get('reply').get('namespace')
write = data.get('write_resource').get('resource')
print ('currently writing to %s' % write )
