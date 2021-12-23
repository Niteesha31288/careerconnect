import json
import boto3
import os
import sys
import subprocess
os.system('pip3 install requests -t /tmp/ --no-cache-dir')
sys.path.insert(1, '/tmp/')
os.system('pip3 install requests_aws4auth -t /tmp/ --no-cache-dir')
sys.path.insert(1, '/tmp/')
import requests
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    try:
        host = 'https://search-forum-svjbgistobczgpqzo4joi3p65e.us-east-1.es.amazonaws.com/threads/_search'
        service = 'es'
        region = 'us-east-1'
        headers = { "Content-Type": "application/json" }
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
        res = requests.get(host, auth=awsauth, headers=headers)
        res = json.loads(res.content.decode('utf-8'))
        print(res)
        thread_list=[]
        for item in res['hits']['hits']:
            document={
                "userid": item['_source']['userid'],
                "userName" :item['_source']['userName'],
                "loggedInEmail": item['_source']['loggedInEmail'],
                "Thread_Title": item['_source']['Thread_Title'],
                "Thread_content": item['_source']['Thread_content'],
                "timestamp": item['_source']['timestamp'],
                "comments":item['_source']['comments'],
                "likes": item['_source']['likes']
            }
            thread_list.append(document)
        print(thread_list)
        return {
            'statusCode': 200,
            'body': json.dumps(thread_list),
            'headers':{ 'Access-Control-Allow-Origin' : '*' }
        }
    except Exception as e:
        print(e)
        return{
            'statusCode': 200,
            'body': json.dumps("event did not come to lambda"),
            'headers':{ 'Access-Control-Allow-Origin' : '*' }
        }