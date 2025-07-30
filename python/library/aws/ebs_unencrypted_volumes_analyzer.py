"""
EBS Encryption Analyzer

This module checks for unencrypted EBS volumes. It generates 
a CSV report and sends it via SES to designated recipients.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class EbsUnencryptedVolumesAnalyzer:
    """
    Analyzes AWS accounts and regions for EBS volumes that are not encrypted.
    Collects data and sends a CSV report via SES.
    """

    def __init__(self, account_id):
        self.account_id = account_id
        self.unencrypted_volumes = []

    def analyze(self, region_list):
        """
        Identifies unencrypted EBS volumes across the specified regions.

        Args:
            region_list (List[str]): A list of AWS regions to scan.
        """
        print("EBS: Analyzing Unecrypted volumes...")

        # Loop through Regions
        for region in region_list:
            ebs = boto3.client('ec2', region_name=region)
            volumes = ebs.describe_volumes()['Volumes']

            for volume in volumes:
                volume_id = volume['VolumeId']
                encrypted = volume['Encrypted']
                volume_type = volume['VolumeType']
                volume_state = volume['State']
                volume_size = volume['Size']
                vol_attachments = ''
                iops = volume['Iops']
                volume_tags = volume.get('Tags', [])
                availability_zone = volume['AvailabilityZone']
                if volume_state == 'in-use':
                    vol_attachments = volume['Attachments'][0]['InstanceId']
                if encrypted is False:
                    self.unencrypted_volumes.append({
                        'Account ID': self.account_id,
                        'Region': region,
                        'Availability Zone': availability_zone,
                        'Volume ID': volume_id,
                        'Encrypted': encrypted,
                        'Type': volume_type,
                        'Attached Instances': vol_attachments,
                        'IOPS': iops,
                        'Size': volume_size,
                    })
        print("EBS: Unencrypted volumes analysis complete")
        print(self.unencrypted_volumes)

        if not self.unencrypted_volumes:
            print("EBS: No unencrypted volumes found.")
            return
        return {
            "csv_data": self.unencrypted_volumes,
            "filename": f"ebs-unencrypted-volumes-{self.account_id}.csv",
            "subject": f"Unencrypted EBS Volumes Detected in AWS Account - {self.account_id}",
            "body_text": f"""
            Hi there,

            As part of our continuous compliance checks, we have identified unencrypted EBS volumes in the AWS account {self.account_id}.

            EBS volumes without encryption exposes workloads to potential data breaches and does not align with security best practices.

            To address this:
            
                1. Review the attached report to see affected volumes by region and usage.
                2. Consider enabling encryption on volumes.
            

            Taking action ensures data confidentiality, strengthens cloud security posture, and aligns with compliance obligations.

            Regards and thanks,
            Atos Managed Services
          """
        }
 

   