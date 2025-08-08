import boto3
import os
import csv
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_TO = json.loads(os.environ.get("EMAIL_TO", "[]"))

def send_email(subject, body_text, attachment_path):
    ses = boto3.client("ses")
    recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = ', '.join(recipients)
    msg.attach(MIMEText(body_text, 'plain'))
    with open(attachment_path, 'rb') as file:
        part = MIMEApplication(file.read())
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg.attach(part)
    try:
        print("Sending email...")
        response = ses.send_raw_email(
            Source=EMAIL_FROM,
            Destinations=recipients,
            RawMessage={'Data': msg.as_string()}
        )
        print("Email sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("Failed to send email:", e)

def write_csv(report):
    if not report or not report.get("csv_data"):
        print("No data to email.")
        return
    data = report["csv_data"]
    filename = report["filename"]
    csv_path = f"/tmp/{filename}"
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    send_email(report["subject"], report["body_text"], csv_path)

def analyze_ebs_unencrypted(account_id, regions, exclusions):
    unencrypted_volumes = []
    excluded_volumes_count = 0
    print("EBS: Analyzing Unecrypted volumes...")
    for region in regions:
        ebs = boto3.client("ec2", region_name=region)
        volumes = ebs.describe_volumes()['Volumes']
        for vol in volumes:
            if vol['VolumeId'] in exclusions.get("ebs_unencrypted_volume_ids", []):
                excluded_volumes_count += 1
                continue
            if not vol['Encrypted']:
                vol_attachments = vol['Attachments'][0]['InstanceId'] if vol['Attachments'] else ''
                unencrypted_volumes.append({
                    "AccountId": account_id,
                    "Region": region,
                    "AvailabilityZone": vol['AvailabilityZone'],
                    "VolumeId": vol['VolumeId'],
                    "Type": vol['VolumeType'],
                    "Encrypted": vol['Encrypted'],
                    "Size": vol['Size'],
                    "IOPS": vol['Iops'],
                    "AttachedInstances": vol_attachments
                })
    print("EBS: Unencrypted volumes analysis complete")
    print(f"EBS: Found {len(unencrypted_volumes)} unencrypted volumes across {len(regions)} regions.")
    print(f"EBS: Excluded {excluded_volumes_count} volumes from the report based on exclusion list.")

    print(unencrypted_volumes)
    print(f"""EBS Encryption Summary:
        - Total unencrypted volumes found: {len(unencrypted_volumes)}
        - Excluded volumes from report: {excluded_volumes_count}
        - Regions scanned: {len(regions)}
    """)

    if not unencrypted_volumes:
        print("EBS: No unencrypted volumes found.")
        return
    return {
            "csv_data": unencrypted_volumes,
            "filename": f"ebs-unencrypted-volumes-{account_id}.csv",
            "subject": f"Unencrypted EBS Volumes Detected in AWS Account - {account_id}",
            "body_text": f"""
            Hi there,

            As part of our continuous compliance checks, we have identified unencrypted EBS volumes in the AWS account {account_id}.

            EBS volumes without encryption exposes workloads to potential data breaches and does not align with security best practices.

            To address this:
            
                1. Review the attached report to see affected volumes by region and usage.
                2. Consider enabling encryption on volumes.
            

            Taking action ensures data confidentiality, strengthens cloud security posture, and aligns with compliance obligations.

            Regards and thanks,
            Atos Managed Services
          """
        }

def analyze_ebs_gp2(account_id, regions, exclusions):
    gp2_volumes = []
    excluded_volumes_count = 0
    print("EBS: Analyzing GP2 volumes...")
    for region in regions:
        ebs = boto3.client("ec2", region_name=region)
        volumes = ebs.describe_volumes()['Volumes']
        for vol in volumes:
            if vol['VolumeId'] in exclusions.get("ebs_gp2_volume_ids", []):
                excluded_volumes_count += 1
                continue
            if vol['VolumeType'] == 'gp2':
                if vol['State'] == 'in-use':
                    vol_attachments = vol['Attachments'][0]['InstanceId']
                gp2_volumes.append({
                    "AccountId": account_id,
                    "Region": region,
                    "AvailabilityZone": vol['AvailabilityZone'],
                    "VolumeId": vol['VolumeId'],
                    "Type": vol['VolumeType'],
                    "Encrypted": vol['Encrypted'],
                    "Size": vol['Size'],
                    "IOPS": vol['Iops'],
                    "AttachedInstances": vol_attachments
                })
    print("EBS: GP2 volumes analysis complete")
    print(f"EBS: Found {len(gp2_volumes)} gp2 volumes across {len(regions)} regions.")
    print(f"EBS: Excluded {excluded_volumes_count} volumes from the report based on exclusion list.")
    print(f"""EBS GP2 Summary:
        - Total gp2 volumes found: {len(gp2_volumes)}
        - Excluded volumes from report: {excluded_volumes_count}
        - Regions scanned: {len(regions)}
    """)

    if not gp2_volumes:
        print("EBS: No GP2 volumes found.")
        return
    return {
            "csv_data": gp2_volumes,
            "filename": f"ebs-gp2-volumes-{account_id}.csv",
            "subject": f"GP2 Volumes Detected in AWS Account - {account_id}",
            "body_text": f"""
            Hi there,

            Our latest audit has found that the AWS account {account_id} is using gp2 EBS volume storage types.

            AWS recommends migrating to gp3 volumes to benefit from:
            
            1. Lower cost per GB and per IOPS
            2. Decoupled IOPS and throughput performance
            3. Greater performance flexibility for modern workloads
            

            Please refer to the attached report for details on affected volumes. We recommend planning a migration to gp3 to optimize performance and cost-efficiency.
            
            Regards and thanks,
            Atos Managed Services
            """
        }

def analyze_security_group_rule(account_id, rule, region, excluded_sg_rules):
    rule_id = rule.get('SecurityGroupRuleId')
    if rule_id in excluded_sg_rules:
        return None, True  # Return excluded flag

    sg_id = rule.get('GroupId')
    direction = 'Ingress' if rule.get('IsEgress') is False else 'Egress'
    protocol = rule.get('IpProtocol')
    from_port = rule.get('FromPort')
    to_port = rule.get('ToPort')

    if protocol == '-1':
        port_range = 'All'
        protocol_name = 'All'
    elif protocol == 'icmp':
        port_range = 'All'
        protocol_name = protocol.upper()
    elif from_port == to_port:
        port_range = str(from_port)
        protocol_name = protocol.upper()
    else:
        port_range = f"{from_port}-{to_port}"
        protocol_name = protocol.upper()

    findings = []
    for cidr, ip_version in [(rule.get('CidrIpv4'), 'IPv4'), (rule.get('CidrIpv6'), 'IPv6')]:
        if cidr in ['0.0.0.0/0', '::/0']:
            findings.append({
                'Account ID': account_id,
                'Region': region,
                'Security Group ID': sg_id,
                'Direction': direction,
                'Protocol': protocol_name,
                'Port Range': port_range,
                'Source/Destination CIDR': cidr,
                'IP Version': ip_version,
                'Rule ID': rule_id
            })

    return findings, False


def analyze_security_group(account_id, regions, exclusions):
    default_sg_rules = []
    excluded_rules_count = 0
    excluded_sg_rules = exclusions.get("security_group_rules", [])

    print("SG: Analyzing for overly permissive rules...")

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        paginator = ec2.get_paginator('describe_security_group_rules')
        page_iterator = paginator.paginate()

        for page in page_iterator:
            sg_rules = page['SecurityGroupRules']

            for rule in sg_rules:
                findings, excluded = analyze_security_group_rule(account_id, rule, region, excluded_sg_rules)
                if excluded:
                    excluded_rules_count += 1
                elif findings:
                    default_sg_rules.extend(findings)
    print(f"SG: Analysis complete. Found {len(default_sg_rules)} risky rules across {len(regions)} regions.")
    print(f"SG: Excluded {excluded_rules_count} rules from the report based on exclusion list.")
    print(default_sg_rules)
    print(f"""SG Summary:
        - Total risky security group rules found: {len(default_sg_rules)}
        - Excluded rules from report: {excluded_rules_count}
        - Regions scanned: {len(regions)})
    """)
    if not default_sg_rules:
        print("SG: No security group with unrestricted rules found.")
        return          
    return {
        "csv_data": default_sg_rules,
        "filename": f"security-group-analysis-{account_id}.csv",
        "subject": f"Security Group Analysis Report for AWS Account - {account_id}",
        "body_text": f"""
        Hi there,

        As part of our ongoing security compliance efforts, we have analyzed the security groups in your AWS account {account_id}.

        The analysis has identified security groups with overly permissive rules that allow unrestricted access.

        Please refer to the attached report for details on affected security groups and rules. We recommend reviewing these rules and applying necessary restrictions to enhance the security posture of your AWS environment. 
        If any rules are not required, consider removing them to minimize the attack surface. And if any unrestricted rules are necessary, let us know so we can update the exclusion list accordingly.

        Regards and thanks,
        Atos Managed Services
        """
    }

def lambda_handler(event, context):
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    enabled_checks = event.get("enabled_checks", [])
    regions = event.get("regions", [])
    exclusions = event.get("exclusions", {})
    print(f"Running for account: {account_id}, Compliance checks in Scope: {enabled_checks}, regions: {regions}")
    if "ebs_unencrypted" in enabled_checks:
        ebs_unecrypted_volumes = analyze_ebs_unencrypted(account_id, regions, exclusions)
        write_csv(ebs_unecrypted_volumes)
    if "ebs_gp2" in enabled_checks:
        ebs_gp2_volumes = analyze_ebs_gp2(account_id, regions, exclusions)
        write_csv(ebs_gp2_volumes)
    if "security_groups" in enabled_checks:
        security_groups = analyze_security_group(account_id, regions, exclusions)
        write_csv(security_groups)
    return {
        'statusCode': 200,
        'body': json.dumps('Compliance module execution complete.')
    }