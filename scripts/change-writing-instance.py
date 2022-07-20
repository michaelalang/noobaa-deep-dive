#!/usr/bin/python3 -W ignore

import requests
import json
import sys
import os
sys.path.append('%s/scripts' %s os.getcwd())
from get_token import get_token

NOOBAA_TOKEN = os.environ.get('TOKEN', get_token())
BUCKET = os.environ.get('BUCKET', 'nsbucket01')

API = os.environ.get('ENDPOINT', 'http://node2.example.com:8080/rpc')
rsp = requests.get(API, json=dict(api='bucket_api', method='list_buckets', params={}, auth_token=NOOBAA_TOKEN))
if not BUCKET in list(map(lambda x: x.get('name'), rsp.json().get('reply').get('buckets'))):
    try:    print ('Bucket %s not configured %s' % (BUCKET, rsp.json().get('reply').get('buckets')))
    except: print (rsp.status_code, rsp.reason)
    sys.exit(1)

rsp = requests.get(API, json=dict(api='bucket_api', method='read_bucket', params=dict(name=BUCKET), auth_token=NOOBAA_TOKEN))
data = rsp.json()
data = data.get('reply').get('namespace')
write = data.get('write_resource').get('resource')
print ('currently writing to %s' % write )
for res in data.get('read_resources'):
    if res.get('resource') != write:
        NEWRESOURCE = res.get('resource')


print ('changing writing to %s' % NEWRESOURCE)
namespace = {'write_resource': {'resource': NEWRESOURCE}, 'read_resources': data.get('read_resources'), 'should_create_underlying_storage': False}
rsp = requests.get(API, json=dict(api='bucket_api', method='update_bucket', params=dict(name=BUCKET, namespace=namespace), auth_token=NOOBAA_TOKEN))

