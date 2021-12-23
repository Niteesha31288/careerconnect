import json
import base64
import boto3
def lambda_handler(event, context):
    # TODO implement
    print(event)
    data = event['img']
    # customlabel = event['customlabels']
    print(data)
    name = event['name']
    token= event['access_token']
    client = boto3.client('cognito-idp', region_name='us-east-1')
    response = client.get_user(
    AccessToken=token
    )
    print(response)
    name1=""
    logInEmail=""
    userid=""
    for attr in response['UserAttributes']:
        if attr['Name'] == 'sub':
            userid= attr['Value']
        if attr['Name'] == 'given_name':
            name1= attr['Value']
        if attr['Name']== 'email':
            logInEmail= attr['Value']
    filename=userid+".pdf"
    s3_resource = boto3.resource('s3')
    obj = s3_resource.Object(bucket_name='resumeparsingdata', key=filename)
    pdf = base64.b64decode(data, validate=True)
    # our S# Bucket
    s3 = boto3.client('s3')
    bucket = 'resumeparsingdata'
    path = '/tmp/'+name
    filename=userid+".pdf"
    handler = open(path, "wb+")
    handler.write(pdf)
    handler.close()
        # upload the temp image to s3
    s3.upload_file(path, bucket, filename, ExtraArgs={'Metadata': {'name': name1, 'logInEmail': logInEmail}})
    return {
        'statusCode': 200,
        'body': json.dumps('Image uploaded successfully')
    }