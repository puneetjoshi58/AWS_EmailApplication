import json
from pipes import Template
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
    
    ses.create_template(
                Template = {
                    'TemplateName': 'notify_customer',
                    'SubjectPart':'Sent by AWS SES',
                    'TextPart':' Marketing Message',
                    'HtmlPart':' Marketing Message'
                }
            )
    
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
            
            ses.verify_email_address(
                EmailAddress= Email_id
            )
            
            response_ses=ses.send_templated_email(
                Source='puneetjoshi58@gmail.com',
                    Destination = {
                        'ToAddresses':[Email_id]
                        #'CcAddresses':[Email_id]
                    },
                    #ReplyToAddresses=[Email_id],
                    Template = 'notify_customer',
                    TemplateData = '{"replace tag name":"with value"}'              
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
