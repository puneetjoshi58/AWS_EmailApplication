
import json
from re import X
import boto3
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)    

Get_Method = 'GET'
Get_Path= '/notify_customer'

dynamo_resource = boto3.resource('dynamodb')
table= dynamo_resource.Table('customer_details')

sns_resource = boto3.client('sns')
topic = sns_resource.create_topic(Name='Marketing_Message')

topic_arn=topic.arn

#response = topic.publish(Message='MyMessage')

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
        
        response = table.get_item(
            Key={
                'customer_id': customer_id
                }
        )
        
        if 'Item' in response:
            
            notification = "Here is the SNS notification for Lambda function tutorial."
            sns_resource.publish (
            PhoneNumber="+919920417755",
            Message = json.dumps({'default': notification}),
            MessageStructure = 'json'
            )
            return buildResponse(200, {'Message': topic_arn})
            
        else :
            return buildResponse(404, {'Message':'CustomerID : %s not found' % customer_id})
    
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

    