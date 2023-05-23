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
            
            items = response_dynamo['Item']
            Email_id = items.get("Email ID")
            
            try:
                ses.verify_email_address(
                EmailAddress= Email_id
                )
                send_email(Email_id)
                return buildResponse(200,{'Message':'email has been sent to : %s !!' % Email_id})
            
            except:
               return buildResponse(200,{'Message':'Confiration email has been sent to : %s !! Confirm the pending email verification and try again' % Email_id})
                
        else :
            return buildResponse(404, {'Message':'CustomerID : %s not found' % customer_id})
    
    except :
        logger.exception('TIP: Try Inserting Customer into Table first')
        
def get_email(Response_Dynamo):
    items = Response_Dynamo['Item']
    Email_id = items.get("Email ID")
    return Email_id

def send_email(email_id):
    ses.send_email(
        Source='puneetjoshi58@gmail.com',
            Destination = {
                #'CcAddresses' : [email_id],
                'ToAddresses' : [email_id]
                
            },
            #ReplyToAddresses = [email_id],
            
            Message = {
                'Subject':{
                    'Data':'Sent by AWS SES',
                    'Charset' : 'utf-8'
                },
                'Body':{
                    'Text':{
                        'Data': 'This is a Marketing Message',
                        'Charset' : 'utf-8'
                    },
                    'Html': {
                        'Data': 'This is a Marketing Message',
                        'Charset' : 'utf-8'
                    }
                }
            }
    )
            
    
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
