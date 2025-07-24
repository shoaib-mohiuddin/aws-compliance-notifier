"""
This module contains the Lambda handler for EBS compliance audits.
It invokes analyzers for unencrypted and gp2 EBS volumes across specified AWS regions,
and emails the results as CSV attachments.
"""
import json
import boto3
from library.ebs.ebs_unencrypted_volumes_analyzer import EBSUnencryptedVolumesAnalyzer
from library.ebs.ebs_gp2_analyzer import EBSGP2Analyzer

def lambda_handler(event, context):
    """
    Entry point for the Lambda function.
    It initializes the analyzers for unencrypted and gp2 EBS volumes.
    """
    print(event, '\n', context)
    regions_list = ['eu-west-1', 'ap-northeast-3']

    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']

    ebs_unecrypted_volumes = EBSUnencryptedVolumesAnalyzer(account_id)
    ebs_unecrypted_volumes.analyze(regions_list)

    ebs_gp2_volumes = EBSGP2Analyzer(account_id)
    ebs_gp2_volumes.analyze(regions_list)

    return {
        'statusCode': 200,
        'body': json.dumps('EBS compliance report completed.')
    }
