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
        jobid= event.get('jobId')
        
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
        response = execute(f'select job_id,  update_date , updates, description from application_updates where user_email = \'{loggedInEmail}\' and job_id = {jobid} order by job_id, update_date')
        listOfAppliedJobs = response.get('records')
        print(len(listOfAppliedJobs[0][0]))
        if len(listOfAppliedJobs[0][0]) == 0:
            body = "Did not find any applications"
        else:
            body = listOfAppliedJobs
                
        
        return {
            'statusCode': 200,
            'body': json.dumps(body)
        }
    except Exception as e:
        print(e)
        return{
            'statusCode' : 500,
            'body' :json.dumps("Something went wrong")
        }


def execute(sql):
    print(sql)
    response = rds_client.execute_statement(
        secretArn=db_credentials_ss_store_arn,
        database=databse_name,
        resourceArn= db_cluster,
        sql=sql)
    print(response)
    return response
