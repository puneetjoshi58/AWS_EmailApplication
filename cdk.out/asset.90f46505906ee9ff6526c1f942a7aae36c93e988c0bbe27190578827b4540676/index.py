import json
import boto3
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)    

client = boto3.resource('dynamodb')
table= client.Table('customer_details')

Get_Method = 'GET'
Post_Method = 'POST'
Patch_Method = 'PATCH'
Delete_Method = 'DELETE'
Health_Path = '/api_health'
CRUD_Customer_Path = '/CRUD_customer'
All_Customers_Path='/All_customers'

def handler(event,context):
    
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    if httpMethod == Get_Method and path == Health_Path:
        response = buildResponse(200)
        
    elif httpMethod == Get_Method and path == CRUD_Customer_Path:
        response = Get_Customer(event['queryStringParameters']['customer_id'])
        
    elif httpMethod == Get_Method and path == All_Customers_Path:
        response = Get_Customers()
        
    elif httpMethod == Post_Method and path == CRUD_Customer_Path:
        response = Create_Customer(json.loads(event['body']))  
        
    elif httpMethod == Patch_Method and path == CRUD_Customer_Path:
        request_body =json.loads(event['body'])
        response = Update_Customer(request_body['customer_id'],request_body['update_key'],request_body['update_value'])
    
    elif httpMethod == Delete_Method and path == CRUD_Customer_Path:
        request_body=json.loads(event['body'])
        response = Delete_Customer(request_body['customer_id'])
        
    else :
        response = buildResponse(404, 'Not Found')
        
    return response
    
    
def Get_Customer(customer_id):
    
    try:
        
        response = table.get_item(
            Key={
                'customer_id': customer_id
                }
        )
        
        if 'Item' in response:
            return buildResponse(200, response['Item'])
            # AND SEND SNS 
        else :
            return buildResponse(404, {'Message':'CustomerID : %s not found' % customer_id})
    
    except :
        logger.exception('TIP: Try Inserting Customer into Table first')
        
def Get_Customers():
    try:
        
        response = table.scan()
        result = response['Items']
        
        while 'Last_Evaluated_Key' in response:
            response = table.scan(Exclusive_Start_Key= response['Last_Evaluated_Key'])
            result.extend(response['Items'])
            
        body={
            'Customers': result 
        }
        return buildResponse(200,body)
    
    except:
        logger.exception('TIP: Check if table is empty')
        
def Create_Customer(request_body):
    try:
        table.put_item(Item=request_body)
         
        body = {
                'Operation' : 'Create Customer',
                'Message' : 'SUCCESS',
                'Item' : request_body
            }
        return buildResponse(200,body)
        
    except:
         logger.exception('TIP: Check for the correct Primary Key')
         
def Update_Customer(customer_id, update_key,update_value ):
    try:
        response = table.update_item(
            Key={
                'customer_id':customer_id
            },
            update_expression =' set %s = :value ' % update_key,
            expression_attribute_value={
                ':value' : update_value
            },
            return_values='UPDATED_NEW'
        )

        body={
            'Operation':'Update',
            'Message':'Success',
            'UpdatedAttributes': response
        }
        
        return buildResponse(200, body)
    except:
        logger.exception('TIP: Try Inserting Customer into Table first')
        
def Delete_Customer(customer_id):
    try:

        response = table.delete_item(                   
            Key={
                'customer_id': customer_id
                },
            ReturnValues = 'ALL_OLD'
        )
        
        body = {                                        
            'Operation' : 'DELETE',
            'Message' : 'SUCCESS',
            'DeletedItem' : response
        }
        
        return buildResponse(200 , body)               
        
        
    except :
        logger.exception('TIP: Check if Item exists in table')
             
    
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