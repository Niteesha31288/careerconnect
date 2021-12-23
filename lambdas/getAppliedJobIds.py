import json
import boto3
import datetime
rds_client = boto3.client('rds-data')
databse_name ='career_connect'
db_cluster = 'arn:aws:rds:us-east-1:561088729535:cluster:database-cloud'
db_credentials_ss_store_arn = 'arn:aws:secretsmanager:us-east-1:561088729535:secret:rds-db-credentials/cluster-I6IRJJTV2OW2EER4PK3CSTPNSQ/postgres-0FkiYR'
def lambda_handler(event, context):
    # TODO implement
    try:
        print(event)
    #{'userEmail': 'virenmparmar@gmail.com', 'jobId': '1234'}
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
        response = execute(f'select job_id from jobs_applied where user_email = \'{loggedInEmail}\';')
        listOfAppliedJobs = response.get('records')
        body = listOfAppliedJobs
        return {
                 'statusCode' :200,
                 'body' : json.dumps(body)
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
    
