#!/usr/bin/python3 -W ignore

import boto3
from time import sleep
import sys
sys.path.append('/root/scripts')
from get_credentials import get_credentials

BUCKET = 'nsbucket01'
API = 'http://node2.example.com:29000'
creds = {'access_key': 'minio2',
         'secret_key': 'minioPassword'}

for r in range(120):
    s3 = boto3.client('s3', aws_access_key_id=creds.get('access_key'), 
			aws_secret_access_key=creds.get('secret_key'), endpoint_url=API, use_ssl=False)
    try:
        for obj in s3.list_objects_v2(Bucket=BUCKET).get('Contents'):
            print (obj.get('Key'))
    except TypeError: pass
    sleep(1)
