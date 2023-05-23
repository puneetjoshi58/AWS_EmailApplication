from email.message import Message
import json
import boto3
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)    

GetMethod = 'GET'
GetPath= '/notify_customer'

def handler(event,context):
    
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    if httpMethod == GetMethod and path == GetPath:
        response = GetName(event['queryStringParameters']['customer_id'])
        
    else :
        response = buildResponse(404, 'NotFound')
        
    return response 
    
    
def GetName(customer_id):
    
    dynamo_resource = boto3.resource('dynamodb')
    table= dynamo_resource.Table('user_data')
    
    sns_resource = boto3.resource('sns')
    try:
        
        response = table.get_item(
            Key={
                'customer_id': customer_id
                }
        )
        
        if 'Item' in response:
            
            notification = "Here is the SNS notification from Lambda function ."
            sns_resource.publish(
                PhoneNumber="+919920417755",
                Message = json.dumps({'default': notification}),
                MessageStructure = 'json'
            )
            return buildResponse(200, response['Item'])
            #return buildResponse(200,{'Message':'Notification has been sent'})
             
            
        else :
            return buildResponse(404, {'Message':'Customer ID : %s not found' %customer_id})
    
    except :
        logger.exception('TIP: Try Inserting Customer into Table first')
        
    
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