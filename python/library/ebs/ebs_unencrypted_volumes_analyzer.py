"""
EBS Encryption Analyzer

This module checks for unencrypted EBS volumes. It generates 
a CSV report and sends it via SES to designated recipients.
"""
import os
import json
import csv
import boto3
from library.helpers.send_email import send_email

sender = os.environ.get('EMAIL_FROM_ADDRESS')
recipients = json.loads(os.environ.get('DEFAULT_EMAIL_RECIPIENTS', '[]'))

class EBSUnencryptedVolumesAnalyzer:
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
                      'Region': region,
                      'Availability Zone': availability_zone,
                      'Volume ID': volume_id,
                      'Encrypted': encrypted,
                      'Type': volume_type,
                      'Attached Instances': vol_attachments,
                      'IOPS': iops,
                      'Size': volume_size,
                      # Define which tags to include in the report - e.g, Name, Owner, Environment
                      'Name': self.get_tag_value(volume_tags, 'Name'),
                      'Owner': self.get_tag_value(volume_tags, 'Owner'),
                      'Environment': self.get_tag_value(volume_tags, 'Environment')
                    })
        print("EBS: Unencrypted volumes analysis complete")
        print(self.unencrypted_volumes)
        if not self.unencrypted_volumes:
            print("EBS: No unencrypted volumes found.")
            return
        print("EBS: Unencrypted volumes found, generating report...")
        self.csv()

    def get_tag_value(self, tags, key):
        """
        Retrieves the value of a specific tag key from the volume tags.
        """
        return next((tag['Value'] for tag in tags if tag['Key'] == key), '')

    def csv(self):
        """
        Generates a CSV report of unencrypted EBS volumes and sends it via email.
        """
        csv_path = f'/tmp/ebs-unencrypted-volumes-{self.account_id}.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Region', 'Availability Zone', 'Volume ID', 'Encrypted',
                          'Type', 'Attached Instances', 'IOPS', 'Size',
                          'Name', 'Owner', 'Environment'] #<-- Define which tags to include in the report
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for volume in self.unencrypted_volumes:
                writer.writerow(volume)
        send_email(
          sender=sender,
          recipients=recipients,
          subject=f'Unencrypted EBS Volumes Detected in AWS Account - {self.account_id}',
          body_text=f"""
          Hi there,

          As part of our continuous compliance checks, we have identified unencrypted EBS volumes in the AWS account {self.account_id}.

          EBS volumes without encryption exposes workloads to potential data breaches and does not align with security best practices.

          To address this:
          
            1. Review the attached report to see affected volumes by region and usage.
            2. Consider enabling encryption on volumes.
          

          Taking action ensures data confidentiality, strengthens cloud security posture, and aligns with compliance obligations.

          Regards and thanks,
          Atos Managed Services
          """,
          attachment_path=csv_path
      )
