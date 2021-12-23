import json
import boto3
import datetime
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
        print(event)
        userid= event['userid']
        comment = event['comment']
        Thread_Title = event['Thread_Title']
        postOfUser= event['postOfUser']
        timestampCreated= event['timestampCreated']
        accessToken = event['access_token']
        client = boto3.client('cognito-idp', region_name='us-east-1')
        response = client.get_user(
        AccessToken=accessToken
        )
        print(response)
        uid=""
        uName=""
        commentTimestamp=str(datetime.datetime.now())
        for attr in response['UserAttributes']:
            if attr['Name']== 'sub':
                uid= attr['Value']
            if attr['Name']== 'given_name':
                uName= attr['Value']
        comment={
            "UserIdOfComment": uid,
            "UserNameOfComment": uName,
            "commentTimestamp": commentTimestamp,
            "comment": comment
        }
        indexid= userid+timestampCreated
        host = 'https://search-forum-svjbgistobczgpqzo4joi3p65e.us-east-1.es.amazonaws.com'
        index = 'threads'
        type = 'lambda-type'
        id= indexid
        url = host + '/' + index + '/' + type +'/'+ id
        service = 'es'
        region = 'us-east-1'
        headers = { "Content-Type": "application/json" }
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
        res = requests.get(url, auth=awsauth, headers=headers)
        res = json.loads(res.content.decode('utf-8'))
        print(res)
        l=len(res['_source']['comments'])
        print(l)
        if l ==0:
            arr= []
            arr.append(comment)
        else:
            arr= res['_source']['comments']
            arr.append(comment)
        document={
            "userid":res['_source']['userid'],
            "userName" :res['_source']['userName'],
            "loggedInEmail": res['_source']['loggedInEmail'],
            "Thread_Title": res['_source']['Thread_Title'],
            "Thread_content": res['_source']['Thread_content'],
            "timestamp": res['_source']['timestamp'],
            "comments": arr,
            "likes": res['_source']['likes']
        }
        response=requests.post(url, auth=awsauth, json=document, headers=headers)
        print(response.content)
    except Exception as e:
        print(e)
        return{
            'statusCode': 200,
            'body': json.dumps("event did not come to lambda"),
            'headers':{ 'Access-Control-Allow-Origin' : '*' }
        }