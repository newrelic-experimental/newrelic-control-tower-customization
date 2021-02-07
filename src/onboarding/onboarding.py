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
import boto3, json, time, os, logging, botocore, uuid
from crhelper import CfnResource
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
session = boto3.Session()

helper = CfnResource(json_logging=False, log_level='INFO', boto_level='CRITICAL', sleep_on_delete=15)

@helper.create
@helper.update
# This module perform the following:
# 1. attempt to create stackset if one does not exist
# 2. attempt to deploy stackset instance to target accounts
def create(event, context):
    logger.info("Onboarding stack launch")
    
    try:
        firstLaunch = False
        stackSetName = os.environ['stackSetName']
        stackSetUrl = os.environ['stackSetUrl']
        newRelicAccId = os.environ['newRelicAccId']
        newRelicSecret = os.environ['newRelicSecret']
        newRelicSQS = os.environ['newRelicSQS']
        managementAccountId = context.invoked_function_arn.split(":")[4]
        cloudFormationClient = session.client('cloudformation')
        regionName = context.invoked_function_arn.split(":")[3]
        cloudFormationClient.describe_stack_set(StackSetName=stackSetName)
        logger.info('Stack set {} already exist'.format(stackSetName))
        helper.Data.update({"result": stackSetName})
        
    except Exception as describeException:
        logger.info('Stack set {} does not exist, creating it now.'.format(stackSetName))
        cloudFormationClient.create_stack_set(
            StackSetName=stackSetName,
            Description='Adds in New Relic integration to your aws accounts. Launch as Stack Set in your Control Tower landing zone management account.',
            TemplateURL=stackSetUrl,
            Parameters=[
                {
                    'ParameterKey': 'NewRelicAccountNumber',
                    'ParameterValue': newRelicAccId,
                    'UsePreviousValue': False,
                    'ResolvedValue': 'string'
                }
            ],
            Capabilities=[
                'CAPABILITY_NAMED_IAM'
            ],
            AdministrationRoleARN='arn:aws:iam::' + managementAccountId + ':role/service-role/AWSControlTowerStackSetRole',
            ExecutionRoleName='AWSControlTowerExecution')
            
        try:
            result = cloudFormationClient.describe_stack_set(StackSetName=stackSetName)
            firstLaunch = True
            logger.info('StackSet {} deployed'.format(stackSetName))
        except cloudFormationClient.exceptions.StackSetNotFoundException as describeException:
            logger.error('Exception getting new stack set, {}'.format(describeException))
            raise describeException
        
        try:
            if firstLaunch and len(os.environ['seedAccounts']) > 0 :
                logger.info("New accounts : {}".format(os.environ['seedAccounts']))
                accountList = os.environ['seedAccounts'].split(",")
                ## TODO: send to SQS and let Lambda pick it
                sqsClient = session.client('sqs')
                messageBatch = []
                for account in accountList:
                    message = {}
                    message['Id'] = str(uuid.uuid4())
                    message['MessageBody'] = json.dumps({ 'accountId': account, 'region': regionName, 'stackSetName': stackSetName})
                    messageBatch.append(message)
                try:
                    sqsResponse = sqsClient.send_message_batch(
                        QueueUrl=newRelicSQS,
                        Entries=messageBatch)
                    logger.info("Queued for stackset instance creation: {}".format(sqsResponse))
                except Exception as sqsException:
                    logger.error("Failed to send queue for stackset instance cration: {}".format(sqsException))
            else:
                logger.info("No additional StackSet instances requested")
        except Exception as create_exception:
            logger.error('Exception creating stack instance with {}'.format(create_exception))
            raise create_exception
        
        helper.Data.update({"result": stackSetName})
        
    # To return an error to cloudformation you raise an exception:
    if not helper.Data.get("result"):
        raise ValueError("Error occured during solution onboarding")
    
    return None #Generate random ID

@helper.delete
# This module perform the following:
# 1. attempt to delete stackset instances
# 2. attempt to delete stackset
def delete(event, context):
    logger.info("Delete StackSet Instances")
    deleteWaitTime = 300
    deleteSleepTime = 30
    try:
        stackSetName = os.environ['stackSetName']
        stackSetUrl = os.environ['stackSetUrl']
        externalId = os.environ['externalId']
        registerSNSTopic = os.environ['registerSNSTopic']
        managementAccountId = context.invoked_function_arn.split(":")[4]
        cloudFormationClient = session.client('cloudformation')
        regionName = context.invoked_function_arn.split(":")[3]
        cloudFormationClient.describe_stack_set(StackSetName=stackSetName)
        logger.info('Stack set {} exist'.format(stackSetName))

        paginator = cloudFormationClient.get_paginator('list_stack_instances')
        pageIterator = paginator.paginate(StackSetName= stackSetName)
        stackSetList = []
        accountList = []
        regionList = []
        for page in pageIterator:
            if 'Summaries' in page:
                stackSetList.extend(page['Summaries'])
        for instance in stackSetList:
            accountList.append(instance['Account'])
            regionList.append(instance['Region'])
        regionList = list(set(regionList))
        accountList = list(set(accountList))
        logger.info("StackSet instances found in region(s): {}".format(regionList))
        logger.info("StackSet instances found in account(s): {}".format(accountList))
        
        try:
            if len(accountList) > 0:
                response = cloudFormationClient.delete_stack_instances(
                    StackSetName=stackSetName,
                    Accounts=accountList,
                    Regions=regionList,
                    RetainStacks=False)
                logger.info(response)
                
                status = cloudFormationClient.describe_stack_set_operation(
                    StackSetName=stackSetName,
                    OperationId=response['OperationId'])
                    
                while status['StackSetOperation']['Status'] == 'RUNNING' and deleteWaitTime>0:
                    time.sleep(deleteSleepTime)
                    deleteWaitTime=deleteWaitTime-deleteSleepTime
                    status = cloudFormationClient.describe_stack_set_operation(
                        StackSetName=stackSetName,
                        OperationId=response['OperationId'])
                    logger.info("StackSet instance delete status {}".format(status))
            
            try:
                response = cloudFormationClient.delete_stack_set(StackSetName=stackSetName)
                logger.info("StackSet template delete status {}".format(response))
            except Exception as stackSetException:
                logger.warning("Problem occured while deleting, StackSet still exist : {}".format(stackSetException))
                
        except Exception as describeException:
            logger.error(describeException)

    except Exception as describeException:
        logger.error(describeException)
        return None
    
    return None #Generate random ID
def lambda_handler(event, context):
    logger.info(json.dumps(event))
    try:
        if 'RequestType' in event: helper(event, context)
    except Exception as e:
        helper.init_failure(e)