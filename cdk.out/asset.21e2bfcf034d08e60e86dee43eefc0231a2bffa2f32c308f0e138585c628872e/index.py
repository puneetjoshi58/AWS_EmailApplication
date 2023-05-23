import json
import boto3
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)    

Get_Method = 'GET'
Get_Path= '/notify_customer'

dynamo_resource = boto3.resource('dynamodb')
table= dynamo_resource.Table('customer_details')

ses = boto3.client('ses')


def handler(event,context):
    
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    if httpMethod == Get_Method and path == Get_Path:
        response = Get_Customer(event['queryStringParameters']['customer_id'])
        
    else :
        response = buildResponse(404, 'NotFound')
        
    return response 
    
def Get_Customer(customer_id):
    
    try:
        response_dynamo = table.get_item(
            Key={
                'customer_id': customer_id
                }
        )
        
        if 'Item' in response_dynamo:
            email_address = get_email
            response_ses=ses.verify_email_address(
                EmailAddress= email_address
            )
            
            return buildResponse(200, response_ses)
            
        else :
            return buildResponse(404, {'Message':'CustomerID : %s not found' % customer_id})
    
    except :
        logger.exception('TIP: Try Inserting Customer into Table first')
        
def get_email(Response_Dynamo):
    items = Response_Dynamo['Item']
    Email_id = items.get("Email ID")
    return Email_id
           
    
def buildResponse(statusCode, body=None):
    response={
    'statusCode' : statusCode,
    'headers':{
         'Content-Type ': 'application/json',
         'Access-Control-Allow-Origin': '*'
    }    
    }
    
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
        
    return response
