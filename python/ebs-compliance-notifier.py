import json
import boto3
from library.ebs.ebs_unencrypted_volumes_analyzer import ebs_unencrypted_volumes_analyzer
from library.ebs.ebs_gp2_analyzer import ebs_gp2_analyzer

def lambda_handler(event, context):
    regions_list = ['eu-west-1', 'ap-northeast-3']

    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']

    ebs_unecrypted_volumes = ebs_unencrypted_volumes_analyzer(account_id)
    ebs_unecrypted_volumes.analyze(regions_list)

    ebs_gp2_volumes = ebs_gp2_analyzer(account_id)
    ebs_gp2_volumes.analyze(regions_list)

    return {
        'statusCode': 200,
        'body': json.dumps('EBS compliance report completed.')
    }
