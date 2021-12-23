
import pdfminer
import pdfminer.high_level
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize
import json
import boto3
from io import BytesIO
import requests
from requests_aws4auth import AWS4Auth



def lambda_handler(event, context):
    # TODO implement
    print(event)
    print("--------S3 Trigger--------------------")
    print(event["Records"][0])
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    name = event["Records"][0]["s3"]["object"]["key"]
    s3_resource = boto3.resource('s3')
    obj = s3_resource.Object(bucket_name=bucket, key=name)
    user_name=obj.get()['Metadata']['name']
    user_logInEmailId= obj.get()['Metadata']['loginemail']
    print("---------------current user details------------")
    print(user_name)
    print(user_logInEmailId)
    fs = obj.get()['Body'].read()
    resume = pdfminer.high_level.extract_text(BytesIO(fs))
    table = boto3.resource('dynamodb',region_name='us-east-1', aws_access_key_id='AKIAYFI36SG745YYIEC2', aws_secret_access_key='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').Table("skillset")
    #obtainedResumeText = fileTextExtractor(resume)
    obtainedResumeText= resume
    finalExtractedEmail , finalExtractedPhone = personalDetailExtractor(obtainedResumeText)
    print("---------------personal details----------------")
    print("Email Address:",finalExtractedEmail)
    print("Phone Number:",finalExtractedPhone)
    firstLetterCapitalizedText,obtainedResumeTextLowerCase,obtainedResumeTextUpperCase = CapitalizeFirstLetter(obtainedResumeText)
    obtainedResumeText = obtainedResumeTextLowerCase + obtainedResumeTextUpperCase + firstLetterCapitalizedText
    obtainedResumeText = re.sub(r'\d+','',obtainedResumeText)
    obtainedResumeText = obtainedResumeText.translate(str.maketrans('','',string.punctuation))
    try:
        print("-----------in try-------------")
        educationLevelList= table.get_item(Key={'skill_d':'education'})
        resumeTechnicalSkillSpecificationList= table.get_item(Key={'skill_d':'skills'})
    except Exception as e:
        print(e)
    extractedEducatioDetails = EducationDetailsExtractor(obtainedResumeText, educationLevelList['Item']['skillname'])
    print("Academic Qualifications:",extractedEducatioDetails)
    filteredTextForSkillExtraction = stopWordRemoval(obtainedResumeText)
    print("---------------filtered text--------------")
    #resumeTechnicalSkillSpecificationList= {'skill':skills }
    technicalSkillScore , technicalSkillExtracted = ResumeSkillExtractor( resumeTechnicalSkillSpecificationList['Item']['skillname'],filteredTextForSkillExtraction)
    print("skills:", technicalSkillExtracted)
    print("score:", technicalSkillScore)
    document = parseForElasticSearch(user_name,user_logInEmailId, finalExtractedEmail,finalExtractedPhone,extractedEducatioDetails,technicalSkillExtracted, technicalSkillScore)
    print(document)
    response = indexIntoES(document, name)
    data = json.loads(response.content.decode('utf-8'))
    return {
        'statusCode': 200,
        'body': json.dumps("hi")
    }
    

def personalDetailExtractor(obtainedResumeText):
    finalExtractedEmail = []
    resumeFinalPhone = []
    oneFourthOfResume = obtainedResumeText[0:len(obtainedResumeText)//4]
    emailResume = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", oneFourthOfResume)
    phoneResume = re.findall(r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})",oneFourthOfResume)
    if len(emailResume) > 1:
        finalExtractedEmail = emailResume[0]
    else:
        finalExtractedEmail = emailResume
    for i in range(len(phoneResume)):
        if len(phoneResume[i])>=10:
            finalExtractedPhone = phoneResume[i]
    return finalExtractedEmail,finalExtractedPhone



firstLetterCapitalizedObtainedResumeText = []
def CapitalizeFirstLetter(obtainedResumeText):
    capitalizingString = " "
    obtainedResumeTextLowerCase = obtainedResumeText.lower()
    obtainedResumeTextUpperCase = obtainedResumeText.upper()
    splitListOfObtainedResumeText = obtainedResumeText.split()
    for i in splitListOfObtainedResumeText:
        firstLetterCapitalizedObtainedResumeText.append(i.capitalize())
    return (capitalizingString.join(firstLetterCapitalizedObtainedResumeText),obtainedResumeTextLowerCase,obtainedResumeTextUpperCase)



def EducationDetailsExtractor(obtainedResumeText, educationLevelList):
    obtainedResumeText.strip('/n')
    newLineRemovedResumeText = obtainedResumeText
    resumeEducationSpecificationList = {'Education':educationLevelList}
    educationExtracted = []
    for area in resumeEducationSpecificationList.keys():
        if area == 'Education':
            educationWord = []
            for word in resumeEducationSpecificationList[area]:
                w1=""
                for w in word.split():
                    if w in obtainedResumeText:
                        w1 += "".join(w+" ")
                educationWord.append(w1)
            for value in educationWord:
                if value.strip() in resumeEducationSpecificationList[area]:
                    educationExtracted.append(value.strip())
    return educationExtracted


def stopWordRemoval(obtainedResumeText):
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(obtainedResumeText)
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    filtered_sentence = [] 
    joinEmptyString = " "
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return(joinEmptyString.join(filtered_sentence))



def ResumeSkillExtractor(resumeTechnicalSkillSpecificationList,filteredTextForSkillExtraction):
    skillScores =0
    skillExtracted = []
    for word in resumeTechnicalSkillSpecificationList:
        if word in filteredTextForSkillExtraction:
            skillExtracted.append(word)
            skillScores +=1
    return skillScores,skillExtracted

def indexIntoES(document, name):
    host = 'https://search-userskills-eatnlhszduvo4cyak2xqwbu2hu.us-east-1.es.amazonaws.com'
    index = 'userskills'
    type = 'lambda-type'
    id=name
    url = host + '/' + index + '/' + type+'/'+id
    service = 'es'
    region = 'us-east-1'
    headers = { "Content-Type": "application/json" }
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    r = requests.post(url, auth=awsauth, json=document, headers=headers)
    return r
    
def parseForElasticSearch(user_name,user_logInEmailId,finalExtractedEmail,finalExtractedPhone,extractedEducatioDetails,technicalSkillExtracted, technicalSkillScore):
    document = {
            "UserName": user_name,
            "User_LoggedInEmail": user_logInEmailId,
            "Email" : finalExtractedEmail,
            "Phone" : finalExtractedPhone,
            "Education": extractedEducatioDetails,
            "skills": technicalSkillExtracted,
            "score" : technicalSkillScore
    }
    return document



