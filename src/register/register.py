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
        stackset_check(payload)

def stackset_check(messages):
    cloudFormationClient = session.client('cloudformation')
    sqsClient = session.client('sqs')
    newRelicRegisterSQS = os.environ['newRelicRegisterSQS']
    
    for stackSetName, params in messages.items():
        logger.info("Checking stack instance status for {}".format(stackSetName))
        try:
            stackset_status = cloudFormationClient.describe_stack_set_operation(
                StackSetName=stackSetName,
                OperationId=params['OperationId']
            )
            if 'StackSetOperation' in stackset_status:
                if stackset_status['StackSetOperation']['Status'] in ['RUNNING','STOPPING','QUEUED',]:
                    logger.info("Stackset operation still running for")
                    
                elif stackset_status['StackSetOperation']['Status'] in ['SUCCEEDED']:
                    logger.info("Start registration")
                    
                elif stackset_status['StackSetOperation']['Status'] in ['FAILED','STOPPED']:
                    logger.warning("Stackset operation failed/stopped")
            
        except Exception as e:
            logger.error(e)
            raise e
        
def lambda_handler(event, context):
    logger.info(json.dumps(event))
    try:
        if 'Records' in event:
            sqs_processing(event['Records'])
    except Exception as e:
        logger.error(e)