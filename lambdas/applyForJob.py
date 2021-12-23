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
        accessToken = event.get('userEmail')        
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
        email = loggedInEmail
        jobId = event.get('jobId')
        response = execute(f'select count(*) as count from jobs_applied where user_email = \'{email}\' and job_id = {jobId};')
        alreadyApplied = response.get('records')[0][0].get('longValue')
        print(alreadyApplied)
        
        if alreadyApplied:
            return {
                 'statusCode' :200,
                 'body' : json.dumps('Already Applied for job')
            }
        
        response = execute(f'insert into jobs_applied(user_email, job_id, date) values(\'{email}\',{jobId},\'{datetime.date.today()}\')') 
        response = execute(f'insert into application_updates(user_email, job_id, update_date, description, updates) values(\'{email}\',{jobId},CURRENT_TIMESTAMP, \'\', \'Initial Application\' )') 
        
        
        
        return {
            'statusCode': 200,
            'body': json.dumps('Applied for the job')
        }
    except Exception as e:
        print(e)
        return{
            'statusCode':500,
            'body':json.dumps('Something went wrong')
        }


def execute(sql):
    response = rds_client.execute_statement(
        secretArn=db_credentials_ss_store_arn,
        database=databse_name,
        resourceArn= db_cluster,
        sql=sql)
    print(response)
    return response
    