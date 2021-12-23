import json
import boto3
import requests
from requests_aws4auth import AWS4Auth


def readFromElastic(email):
    '''
    host = 'https://search-userskills-eatnlhszduvo4cyak2xqwbu2hu.us-east-1.es.amazonaws.com'
    index = 'userskills'
    type = 'lambda-type'
    url = host + '/' + index + '/' + type
    service = 'es'
    region = 'us-east-1'
    headers = { "Content-Type": "application/json" }
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    '''
    host ='https://search-userskills-eatnlhszduvo4cyak2xqwbu2hu.us-east-1.es.amazonaws.com/userskills/_search?q=' + email.split('@')[0]
    index = 'userskills'
    type = 'lambda-type'
    url = host + '/' + index + '/' + type
    service = 'es'
    region = 'us-east-1'
    headers = { "Content-Type": "application/json" }
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    res = requests.get(host, auth=awsauth, headers=headers)
    res = json.loads(res.content.decode('utf-8'))
    print(res)
    res =  res["hits"]["hits"]
    skills = res[0]['_source']['skills']
    print(skills)
    return skills
    
def findJobs(skills):
    
    headers = {"Content-Type":"application/json"}
    jobs = []
    hits = []
    skills = ['Python']
    for skill in skills:
        print('This is skills')
        print(skill)
        try:
            host = 'https://search-jobskill-nqg6msu332lr2qmjpjtlgemwhi.us-east-1.es.amazonaws.com/jobids/_doc/_search?q=' + str(skill)
            service = 'es'
            region = 'us-east-1'
            headers = { "Content-Type": "application/json" }
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
            res = requests.get(host, auth=awsauth, headers=headers)
            res = json.loads(res.content.decode('utf-8'))
            jobIds =  res.get('hits').get('hits')
            print(jobIds)
            for job in jobIds:
                jobs.append(job.get('_source').get('jobids'))
            jobs = set(jobs)
            print(jobs)
            # response = requests.get(host,headers=headers,auth=('', ''))
            # print('inside fnidjobs try')
            # print(response)
            # response = json.loads(response.content.decode('utf-8'))
            # print(response)
            # hits = response.get('hits').get('hits')
        except Exception as e:
            print(e)
        print(hits)
        for hit in hits:
            job_id = hit.get('_source').get('id')
            jobs.add(job_id)
    return jobs
    
def jobDescription(jobs):
    print('iside')
    print(jobs)
    jobData = []
    table = boto3.resource('dynamodb',region_name='us-east-1', aws_access_key_id='', aws_secret_access_key='').Table("jobs")
    print('here i am')
    for job in jobs:
        print(job)
        response = table.get_item(Key={'jobbed': str(job)})
        print(response)
        jobData.append({'job_id' : job ,'job_title':response['Item']['job_title'], 'min_salary':  response['Item']['min_salary'], 'description' : response['Item']['job_desc']})
    print(jobData)
    return jobData

def lambda_handler(event, context):
    # TODO implement
    print(event)
    accessToken = event.get('token')
    
    client = boto3.client('cognito-idp', region_name='us-east-1')
    response = client.get_user(
    AccessToken=accessToken
    )
    print(response)
    loggedInEmail = ''
    for attr in response['UserAttributes']:
        if attr['Name'] == 'email':
            loggedInEmail = attr['Value']
            break
    print(loggedInEmail)
    jobData = []
    skills = readFromElastic(loggedInEmail)
    skills = set(skills)
    job = findJobs(skills)
    jobData = jobDescription(job)
    return {
        'statusCode': 200,
        'body': json.dumps(jobData)
    }
