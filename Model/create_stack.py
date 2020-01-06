import logging
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError


cf = boto3.client('cloudformation')
log = logging.getLogger('deploy.cf.create_or_update')
stack_status = ['ROLLBACK_COMPLETE', 'ROLLBACK_FAILED', 'DELETE_FAILED', 'UPDATE_ROLLBACK_COMPLETE']


def create(stack_name, template, parameters):
    """Update or create stack"""

    template_data = template
    parameter_data = parameters

    params = {
        'StackName': stack_name,
        'TemplateURL': template_data,
        'Parameters': parameter_data,
        'Capabilities': ['CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
    }

    try:
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            stack_result = cf.update_stack(**params)
            waiter = cf.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            stack_result = cf.create_stack(**params)
            waiter = cf.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)
    except ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise
    else:
        print(json.dumps(
            cf.describe_stacks(StackName=stack_result['StackId']),
            indent=2,
            default=json_serial
        ))


def _stack_exists(stack_name):
    stacks = cf.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack == any(stack_status):
            cf.delete_stack(StackName=stack_name)
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def delete_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for key in bucket.objects.all():
        key.delete()
    bucket.delete()
