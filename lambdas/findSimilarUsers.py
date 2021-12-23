import json
import boto3
import requests
from requests_aws4auth import AWS4Auth


def findSkills():
    data=[]
    host = 'https://search-userskills-eatnlhszduvo4cyak2xqwbu2hu.us-east-1.es.amazonaws.com/userskills/_search'
    service = 'es'
    region = 'us-east-1'
    headers = { "Content-Type": "application/json" }
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    res = requests.get(host, auth=awsauth, headers=headers)
    res = json.loads(res.content.decode('utf-8'))
    data= res["hits"]["hits"]
    #print("-------------user list with skills------------------")
    #print(data)
    return data
    
    
def getUserDetail(res, loggedInEmail):
    #print(email)
    userSkillToMatch=[]
    for user in res:
        if user['_source']['User_LoggedInEmail']== loggedInEmail:
            userSkillToMatch= user['_source']['skills']
    print("----------------skills to match------------------")
    print(userSkillToMatch)
    return userSkillToMatch
    
def getUserListWithMatchingSkills(res, userSkillToMatch, loggedInEmail):
    UserListWithMatchedSkills=[]
    a=set(userSkillToMatch)
    for user in res:
        userdict={}
        if user['_source']['User_LoggedInEmail'] != loggedInEmail:
            b= set(user['_source']['skills'])
            c= list(set(a) & set(b))
            userdict["Name"]= user['_source']['UserName']
            userdict['LoggedInEmail']= user['_source']['User_LoggedInEmail']
            userdict["Email"]= user['_source']['Email'][0]
            userdict["Matchskills"]= c
            userdict["noOfMatchedSkills"]= len(c)
            UserListWithMatchedSkills.append(userdict)
    print("----------users with matching skills--------------")
    print(UserListWithMatchedSkills)
    return UserListWithMatchedSkills
    
            
        
            
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
    res = findSkills()
    print(res)
    userSkillToMatch=getUserDetail(res, loggedInEmail)
    UserListWithMatchedSkills= getUserListWithMatchingSkills(res, userSkillToMatch, loggedInEmail)
    
    return {
        'statusCode': 200,
        'body': json.dumps(UserListWithMatchedSkills)
    }
