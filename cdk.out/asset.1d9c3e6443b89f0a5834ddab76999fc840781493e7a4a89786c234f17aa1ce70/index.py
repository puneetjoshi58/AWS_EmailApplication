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

sns = boto3.resource('sns')
topic = sns.create_topic(Name='Marketing_Message')
topic_arn=topic.arn

sns_client = boto3.client('sns')

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
            
            #PhNo=get_number(response_dynamo)
            #register_phone_number(PhNo)
            #response_sns_sms= sns_publish_sms(PhNo)
            
            email_id= get_email(response_dynamo)
            sns_subscribe(email_id)
            response_sns_topic= sns_publish_topic()
            
            return buildResponse(200, response_sns_topic)
            
        else :
            return buildResponse(404, {'Message':'CustomerID : %s not found' % customer_id})
    
    except :
        logger.exception('TIP: Try Inserting Customer into Table first')
        
def get_email(Response_Dynamo):
    items = Response_Dynamo['Item']
    Email_id = items.get("Email ID")
    return Email_id
           
def sns_subscribe(EmailID):
    sns_client.subscribe(
                TopicArn= topic_arn,
                Protocol='email',
                Endpoint = EmailID
                )
                
def sns_publish_topic():
    notification = "Here is the SNS notification for Lambda function tutorial."
    response_sns_topic =sns_client.publish (
            TopicArn= topic_arn,
            Message = json.dumps({'default': notification}),
            Subject = 'Sent by AWS SNS',
            MessageStructure = 'json'
            )
    return response_sns_topic
    
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

def get_number(Response_Dynamo):
    items = Response_Dynamo['Item']
    Phone_Number = items.get("Phone_Number")
    return Phone_Number

def sns_publish_sms(PhNo):
    notification = "Here is the SNS notification for Lambda function tutorial."
    response_sns_sms =sns_client.publish (
            PhoneNumber=PhNo,
            Message = json.dumps({'default': notification}),
            Subject = 'Sent by AWS SNS',
            MessageStructure = 'json'
            )
    return response_sns_sms

def register_phone_number(PhNo):
    sns_client.create_sms_sandbox_phone_number(
            PhoneNumber= PhNo,
            LanguageCode='en-US'
        )
