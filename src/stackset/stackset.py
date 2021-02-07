#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import boto3, json, time, os, logging, botocore
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
session = boto3.Session()

def sqs_processing(messages):
    target_stackset = {}
    for message in messages:
        payload = json.loads(message['body'])
        stackset_processing(payload)
    
def stackset_processing(messages):
    cloudFormationClient = session.client('cloudformation')
    sqsClient = session.client('sqs')
    newRelicStackSQS = os.environ['newRelicStackSQS']
    newRelicRegisterSQS = os.environ['newRelicRegisterSQS']
    
    for stackSetName, params in messages.items():
        logger.info("Processing stack instances for {}".format(stackSetName))
        param_accounts = params['target_accounts']
        param_regions = params['target_regions']
        logger.info("Target accounts : {}".format(param_accounts))
        logger.info("Target regions: {}".format(param_regions))
        
        try:
            stack_operations = True
            cloudFormationClient.describe_stack_set(StackSetName=stackSetName)
            cloudFormationPaginator = cloudFormationClient.get_paginator('list_stack_set_operations')
            stackset_iterator = cloudFormationPaginator.paginate(
                StackSetName=stackSetName
            )
            for page in stackset_iterator:
                if 'Summaries' in page:
                    for operation in page['Summaries']:
                        if operation['Status'] in ('RUNNING', 'STOPPING'):
                            stack_operations = False
                            break
                    if stack_operations == False: 
                        break
            
            if stack_operations:
                response = cloudFormationClient.create_stack_instances(StackSetName=stackSetName, Accounts=param_accounts, Regions=param_regions)
                logger.info("StackSet instance created {}".format(response))
                messageBody = {}
                messageBody[stackSetName] = {'OperationId': response['OperationId']}
                try:
                    sqsResponse = sqsClient.send_message(
                        QueueUrl=newRelicRegisterSQS,
                        MessageBody=json.dumps(messageBody))
                    logger.info("Queued for registration: {}".format(sqsResponse))
                except Exception as sqsException:
                    logger.error("Failed to send queue for registration: {}".format(sqsException))                
            else:
                ## TODO: send message back to SQS
                logger.warning("Existing StackSet operations still running")
                messageBody = {}
                messageBody[stackSetName] = messages[stackSetName]
                try:
                    sqsResponse = sqsClient.send_message(
                        QueueUrl=newRelicStackSQS,
                        MessageBody=json.dumps(messageBody))
                    logger.info("Re-queued for stackset instance creation: {}".format(sqsResponse))
                except Exception as sqsException:
                    logger.error("Failed to send queue for stackset instance creation: {}".format(sqsException))

        except cloudFormationClient.exceptions.StackSetNotFoundException as describeException:
            logger.error('Exception getting stack set, {}'.format(describeException))
            raise describeException

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    try:
        if 'Records' in event:
            sqs_processing(event['Records'])
    except Exception as e:
        logger.error(e)