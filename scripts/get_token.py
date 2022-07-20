#!/usr/bin/python3 -W ignore
  
import requests
import json
import os, sys
import getpass

def get_token(interactive=False):
	if interactive == True:
		password = getpass.getpass().strip()
	else:	password = os.environ.get('PWD')
	API = os.environ.get('ENDPOINT', 'http://node2.example.com:8080/rpc')
	rsp = requests.get(API, json=dict(api='auth_api', method='create_auth', params=dict(
	                    email=os.environ.get('EMAIL', 'milang@redhat.com'),
	                    password=password,
	                    system=os.environ.get('SYSTEM', 'test')),
	                    auth_token=''))
	try:
	    return rsp.json().get('reply').get('token')
	except:
	    return (rsp.status_code, rsp.text)
	    sys.exit(1)

if __name__ == '__main__':
	print(get_token(interactive=True))
