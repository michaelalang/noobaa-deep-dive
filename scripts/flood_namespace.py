#!/usr/bin/python3 -W ignore

import boto3
from time import sleep
import sys
import os
sys.path.append('%s/scripts' % os.getcwd())
from get_credentials import get_credentials

BUCKET = os.environ.get('BUCKET', 'nsbucket01')
API = os.environ.get('ENDPOINT', 'http://node2.example.com:6001')
creds = get_credentials()

s3 = boto3.client('s3', aws_access_key_id=creds.get('access_key'), 
 	  	  aws_secret_access_key=creds.get('secret_key'), endpoint_url=API, use_ssl=False)
counter = 0
errcounter = 0
for r in range(2000):
    try:
        s3.put_object(ACL='public-read', Bucket=BUCKET, 
                      Key='file%s' % r, Body='file%s' % r).get('ResponseMetadata').get('RequestId')
    except: 
        errcounter += 1
    sleep(0.05)

print('Requests: %i Errors: %i' % (r, errcounter))
