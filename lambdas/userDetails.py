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
    # TODO implement
    try:
        print(event)
        accessToken = event['queryStringParameters']['token']
        client = boto3.client('cognito-idp', region_name='us-east-1')
        response = client.get_user(
        AccessToken=accessToken
        )
        print(response)
        loggedInEmail = ''
        userid=""
        for attr in response['UserAttributes']:
            if attr['Name']== 'sub':
                userid= attr['Value']
            if attr['Name'] == 'email':
                loggedInEmail = attr['Value']
                break
        print(loggedInEmail)
        host = 'https://search-userskills-eatnlhszduvo4cyak2xqwbu2hu.us-east-1.es.amazonaws.com'
        index = 'userskills'
        type = 'lambda-type'
        id=userid+".pdf"
        url = host + '/' + index + '/' + type+'/'+id
        service = 'es'
        region = 'us-east-1'
        headers = { "Content-Type": "application/json" }
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
        res = requests.get(url, auth=awsauth, headers=headers)
        res = json.loads(res.content.decode('utf-8'))
        #print(res)
        data= res["_source"]
        #print("-------------user list with skills------------------")
        print(data)
        
        return {
        'statusCode': 200,
        'body': json.dumps(data),
        'headers':{ 'Access-Control-Allow-Origin' : '*' }
        }
    except:
        return{
            'statusCode': 200,
            'body': json.dumps("event did not come to lambda"),
            'headers':{ 'Access-Control-Allow-Origin' : '*' }
        }