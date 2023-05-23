from constructs import Construct
from aws_cdk import (
    CfnParameter,
    Duration,
    Stack,
    aws_iam as _iam,
    aws_dynamodb as _dynamodb,
   aws_lambda as _lambda,
   aws_apigateway as _apigateway,
    aws_sns as _sns,
    aws_sns_subscriptions as _subs,
)


class MessageSchedulingAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        customer_details = _dynamodb.Table(self,id='customer_id',table_name='customer_details',
                                  partition_key= _dynamodb.Attribute(name = 'customer_id', type= _dynamodb.AttributeType.STRING))
        
        enable_message_scheduling = _iam.Role(self, "enable_message_scheduling",
            assumed_by= _iam.ServicePrincipal("lambda.amazonaws.com")
            )
        
        enable_message_scheduling.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess"))
        enable_message_scheduling.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"))
        enable_message_scheduling.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayAdministrator"))
        enable_message_scheduling.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambda_FullAccess"))
        enable_message_scheduling.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"))
        enable_message_scheduling.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSESFullAccess"))
        
        customer_handler = _lambda.Function(self, id='customer_handler',runtime= _lambda.Runtime.PYTHON_3_9,
                                     handler='index.handler',
                                     code=_lambda.Code.from_asset('Customer_Handler'),
                                     role=enable_message_scheduling
                                     )
        
        send_sns = _lambda.Function(self, id='send_ses',runtime= _lambda.Runtime.PYTHON_3_9,
                                    handler='index.handler',
                                    code=_lambda.Code.from_asset('Send_SES'),
                                    role=enable_message_scheduling
                                    )
        
        CRUD_Customer = _apigateway.LambdaRestApi(self,id='CRUD_customer',rest_api_name='CRUD_customer',handler = customer_handler)
        CRUD_customer = CRUD_Customer.root.add_resource('CRUD_customer')
        CRUD_customer.add_method('POST')
        CRUD_customer.add_method('GET')
        CRUD_customer.add_method('PATCH')
        CRUD_customer.add_method('DELETE')
        
        All_Customers = _apigateway.LambdaRestApi(self,id='all_customers',rest_api_name='all_customers',handler = customer_handler)
        All_customers = All_Customers.root.add_resource('all_customers')
        All_customers.add_method('GET')
        
        Notify_Customer = _apigateway.LambdaRestApi(self,id='notify_customer',rest_api_name='notify_customer',handler = send_sns)
        notify_customer = Notify_Customer.root.add_resource('notify_customer')
        notify_customer.add_method('GET')
        
        
        
       
        
        
        
        

        
        
        
        
        
        
        
        