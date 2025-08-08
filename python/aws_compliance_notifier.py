"""
This module contains the Lambda handler for EBS compliance audits.
It invokes analyzers for unencrypted and gp2 EBS volumes across specified AWS regions,
and emails the results as CSV attachments.
"""
import os
import json
import boto3
from library.aws.ebs_unencrypted_volumes_analyzer import EbsUnencryptedVolumesAnalyzer
from library.aws.ebs_gp2_analyzer import EbsGP2Analyzer
from library.aws.security_group_analyzer import SecurityGroupAnalyzer
from library.helpers.assume_role import assume_role
from library.helpers.write_csv import write_csv


def lambda_handler(event, context):
    """
    Entry point for the Lambda function.
    It initializes the analyzers for modules specified in the event.
    """

    account_id = event.get("account_id")
    regions = event.get("regions", [])
    enabled_checks = event.get("enabled_checks", [])
    exclusions = event.get("exclusions", {
        "ebs_gp2_volume_ids": [],
        "ebs_unencrypted_volume_ids": [],
        "security_group_rule_ids": []
    })

    # Assume role in the target account
    session = assume_role(account_id)

    print(f"Running for account: {account_id}, Compliance checks in Scope: {enabled_checks}, regions: {regions}")

    if "ebs_unencrypted" in enabled_checks:
        ebs_unecrypted_volumes = EbsUnencryptedVolumesAnalyzer(account_id, session, exclusions).analyze(regions)
        write_csv(ebs_unecrypted_volumes)

    if "ebs_gp2" in enabled_checks:
        ebs_gp2_volumes = EbsGP2Analyzer(account_id, session, exclusions).analyze(regions)
        write_csv(ebs_gp2_volumes)

    if "security_groups" in enabled_checks:
        security_groups = SecurityGroupAnalyzer(account_id, session, exclusions).analyze(regions)
        write_csv(security_groups)

    return {
        'statusCode': 200,
        'body': json.dumps('Compliance module execution complete.')
    }
