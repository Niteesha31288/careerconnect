import json
import requests
import boto3
from requests_aws4auth import AWS4Auth
def lambda_handler(event, context):
    # TODO implement
    host = 'https://search-forum-svjbgistobczgpqzo4joi3p65e.us-east-1.es.amazonaws.com/threads'
    service = 'es'
    region = 'us-east-1'
    headers = { "Content-Type": "application/json" }
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    res = requests.delete(host, auth=awsauth, headers=headers)
    #res = json.loads(res.content.decode('utf-8'))
    print(res)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
