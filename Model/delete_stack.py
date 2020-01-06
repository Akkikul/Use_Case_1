import boto3
from botocore.exceptions import ClientError


buckets = '[constants.host_bucket]'
stack_name = 'use-case-2'


def delete_stack(buckets, stack_name):
    s3 = boto3.resource('s3')
    cf = boto3.client('cloudformation')
    try:
        for bucket_name in buckets:
            bucket = s3.Bucket(bucket_name)
            for key in bucket.objects.all():
                key.delete()
            bucket.delete()
        cf.delete_stack(StackName=stack_name)
    except ClientError as e:
        print(f"Error: {e} occur")


delete_stack(buckets, stack_name)
