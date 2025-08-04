"""
This module contains the Lambda handler for EBS compliance audits.
It invokes analyzers for unencrypted and gp2 EBS volumes across specified AWS regions,
and emails the results as CSV attachments.
"""
import os
import json
import boto3
from library.helpers.write_csv_and_email import write_csv_and_email
from library.aws.ebs_unencrypted_volumes_analyzer import EbsUnencryptedVolumesAnalyzer
from library.aws.ebs_gp2_analyzer import EbsGP2Analyzer
from library.aws.security_group_analyzer import SecurityGroupAnalyzer


def lambda_handler(event, context):
    """
    Entry point for the Lambda function.
    It initializes the analyzers for modules specified in the event.
    """

    account_id = event.get("account_id")
    regions = event.get("regions", [])
    modules_in_scope = event.get("modules_in_scope", [])
    exclusions = event.get("exclusions", {
        "ebs_gp2_volume_ids": [],
        "ebs_unencrypted_volume_ids": [],
        "security_group_rule_ids": []
    })

    sender = os.environ.get('EMAIL_FROM')
    recipients = json.loads(os.environ.get('EMAIL_TO', '[]'))

    print(f"Running for account: {account_id}, Modules in Scope: {modules_in_scope}, regions: {regions}")

    if "ebs_unencrypted" in modules_in_scope:
        ebs_unecrypted_volumes = EbsUnencryptedVolumesAnalyzer(account_id, exclusions).analyze(regions)
        write_csv_and_email(sender, recipients, ebs_unecrypted_volumes)

    if "ebs_gp2" in modules_in_scope:
        ebs_gp2_volumes = EbsGP2Analyzer(account_id, exclusions).analyze(regions)
        write_csv_and_email(sender, recipients, ebs_gp2_volumes)

    if "security_groups" in modules_in_scope:
        security_groups = SecurityGroupAnalyzer(account_id, exclusions).analyze(regions)
        write_csv_and_email(sender, recipients, security_groups)

    return {
        'statusCode': 200,
        'body': json.dumps('Compliance module execution complete.')
    }


# sender = os.environ.get('EMAIL_FROM_ADDRESS')
# recipients = json.loads(os.environ.get('DEFAULT_EMAIL_RECIPIENTS', '[]'))

# regions = ['eu-west-1', 'ap-northeast-3']

# sts = boto3.client('sts')
# account_id = sts.get_caller_identity()['Account']
# security_groups = SecurityGroupAnalyzer(account_id).analyze(regions)
# write_csv_and_email(sender, recipients, security_groups)

# ebs_unecrypted_volumes = EbsUnencryptedVolumesAnalyzer(account_id).analyze(regions)
# write_csv_and_email(sender, recipients, ebs_unecrypted_volumes)

# ebs_gp2_volumes = EbsGP2Analyzer(account_id).analyze(regions)
# write_csv_and_email(sender, recipients, ebs_gp2_volumes)



# session = assume_role(account_id)

# if "ebs_unencrypted" in modules_in_scope:
#     ebs_unecrypted_volumes = EbsUnencryptedVolumesAnalyzer(account_id, session).analyze(regions)
#     write_csv_and_email(sender, recipients, ebs_unecrypted_volumes)