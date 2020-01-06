import boto3
import os
import zipfile
from Controller import constants
from botocore.exceptions import ClientError
from Model.create_stack import create


s3_client = boto3.client('s3', region_name=constants.region)
template_url = f"https://{constants.host_bucket}.s3.{constants.region}.amazonaws.com/{constants.temp_name}"
parameters = [dict(ParameterKey="HostBucket", ParameterValue=constants.host_bucket)]


def execute_script():
    try:
        location = {'LocationConstraint': constants.region}
        s3_client.create_bucket(Bucket=constants.host_bucket, CreateBucketConfiguration=location)
        upload_directory(constants.path, constants.host_bucket)
        upload_zip(constants.host_bucket, constants.folder_name)
        return True
    except ClientError as e:
        print(f"Error: {e} occur")
        return False


def upload_directory(path, bucket):
    for root, dirs, files in os.walk(path):
        for file in files:
            s3_client.upload_file(os.path.join(root, file), bucket, file)


def upload_zip(host_bucket, folder_name):
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            zip_file = zipfile.ZipFile(os.path.splitext(file)[0] + '.zip', "w")
            zip_file.write(os.path.join(folder_name, file), file)
            zip_file.write(os.path.join(constants.model_folder_name, 'rds_config.py'), 'Model/rds_config.py')
            for fn in os.listdir(constants.dep_folder_name):
                if fn == 'constants':
                    for subfn in os.listdir(constants.dep_folder_name + '/constants'):
                        zip_file.write(os.path.join(constants.dep_folder_name + '/constants', subfn),
                                       'pymysql/constants/' + subfn)
                else:
                    zip_file.write(os.path.join(constants.dep_folder_name, fn), 'pymysql/' + fn)
            zip_file.close()
            s3_client.upload_file(os.path.splitext(file)[0] + '.zip', host_bucket, os.path.splitext(file)[0] + '.zip')
            os.remove(os.path.splitext(file)[0] + '.zip')


if __name__ == "__main__":
    response = execute_script()
    if response:
        create(constants.stack_name, template_url, parameters)
    else:
        print('Stack Creation Failed')

