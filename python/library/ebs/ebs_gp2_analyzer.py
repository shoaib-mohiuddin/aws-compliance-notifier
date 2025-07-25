"""
EBS GP2 Analyzer

This module checks for EBS volumes that are gp2 type. It generates 
a CSV report and sends it via SES to designated recipients.
"""
import os
import json
import csv
import boto3
from library.helpers.send_email import send_email

sender = os.environ.get('EMAIL_FROM_ADDRESS')
recipients = json.loads(os.environ.get('DEFAULT_EMAIL_RECIPIENTS', '[]'))

class EBSGP2Analyzer:
    """
    Identifies EBS volumes still using gp2 and generates reports.
    """

    def __init__(self, account_id):
        self.account_id = account_id
        self.gp2_volumes = []

    def analyze(self, region_list):
        """
        Identifies EBS volumes that are gp2 type across the specified regions.

        Args:
            region_list (List[str]): A list of AWS regions to scan.
        """
        print("EBS: Analyzing GP2 volumes...")

        # Loop through Regions
        for region in region_list:

            ebs = boto3.client('ec2', region_name=region)
            volumes = ebs.describe_volumes()['Volumes']

            for volume in volumes:
                volume_id = volume['VolumeId']
                volume_type = volume['VolumeType']
                volume_state = volume['State']
                volume_size = volume['Size']
                availability_zone = volume['AvailabilityZone']
                vol_attachments = ''
                iops = volume['Iops']
                volume_tags = volume.get('Tags', [])
                if volume_type == 'gp2':
                    if volume_state == 'in-use':
                        vol_attachments = volume['Attachments'][0]['InstanceId']
                    self.gp2_volumes.append({
                        'Region': region,
                        'Availability Zone': availability_zone,
                        'Volume ID': volume_id,
                        'Type': volume_type,
                        'Attached Instances': vol_attachments,
                        'IOPS': iops,
                        'Size': volume_size,
                        # Define which tags to include in the report - e.g, Name, Owner, Environment
                        'Name': self.get_tag_value(volume_tags, 'Name'),
                        'Owner': self.get_tag_value(volume_tags, 'Owner'),
                        'Environment': self.get_tag_value(volume_tags, 'Environment')
                    })
        print("EBS: GP2 volumes analysis complete")
        print(self.gp2_volumes)
        if not self.gp2_volumes:
            print("EBS: No GP2 volumes found.")
            return
        print("EBS: GP2 volumes found, generating report...")
        self.csv()

    def get_tag_value(self, tags, key):
        """
        Retrieves the value of a specific tag key from the volume tags.
        """
        return next((tag['Value'] for tag in tags if tag['Key'] == key), '')

    def csv(self):
        """
        Generates a CSV report of gp2 EBS volumes and sends it via email.
        """
        csv_path = f'/tmp/ebs-gp2-volumes-{self.account_id}.csv'
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Region', 'Availability Zone', 'Volume ID', 'Type',
                          'Size', 'IOPS', 'Attached Instances',
                          'Name', 'Owner', 'Environment'] #<-- Define which tags to include in the report
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for volume in self.gp2_volumes:
                writer.writerow(volume)

        send_email(
            sender=sender,
            recipients=recipients,
            subject=f'GP2 Volumes Detected in AWS Account - {self.account_id}',
            body_text=f"""
            Hi there,

            Our latest audit has found that the AWS account {self.account_id} is using gp2 EBS volume storage types.

            AWS recommends migrating to gp3 volumes to benefit from:
            
            1. Lower cost per GB and per IOPS
            2. Decoupled IOPS and throughput performance
            3. Greater performance flexibility for modern workloads
            

            Please refer to the attached report for details on affected volumes. We recommend planning a migration to gp3 to optimize performance and cost-efficiency.

            Regards and thanks,
            Atos Managed Services
            """,
            attachment_path=csv_path
        )
