import json
import boto3
import datetime
rds_client = boto3.client('rds-data')
databse_name =''
db_cluster = ''
db_credentials_ss_store_arn = ''

def lambda_handler(event, context):
    # TODO implement
    try:
        print(event)
        accessToken = event.get('userId')
        
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
    # userId, description, updateState, jobId
        userid = event.get('userId')
        jobid = event.get('jobId')
        description = event.get('description')
        updateState = event.get('updateState')
        
        response = execute(f'insert into application_updates(user_email, job_id, update_date, description, updates) values(\'{loggedInEmail}\',{jobid}, CURRENT_TIMESTAMP,\'{description}\', \'{updateState}\' );')
        return {
            'statusCode': 200,
            'body': json.dumps('Sussfully updated')
        }
    except Exception as e:
        print(e)
        return{
            'statusCode' : 500,
             'body': json.dumps('Something went Worng')
        }


def execute(sql):
    response = rds_client.execute_statement(
        secretArn=db_credentials_ss_store_arn,
        database=databse_name,
        resourceArn= db_cluster,
        sql=sql)
    print(response)
    return response
    
