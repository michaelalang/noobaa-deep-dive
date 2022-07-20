#!/usr/bin/python3 -W ignore
  
import requests
import json
import os, sys
import getpass

def get_credentials():
	API = os.environ.get('ENDPOINT', 'http://node2.example.com:8080/rpc')
	rsp = requests.get(API, json=dict(api='account_api', method='read_account', params=dict(
	                    email=os.environ.get('EMAIL', 'milang@redhat.com')),
	                    auth_token=os.environ.get('TOKEN')))
	try:
	    return rsp.json().get('reply').get('access_keys')[0]
	except:
	    return dict(access_key=rsp.status_code, secret_key=rsp.text)

if __name__ == '__main__':
	print(get_credentials())
