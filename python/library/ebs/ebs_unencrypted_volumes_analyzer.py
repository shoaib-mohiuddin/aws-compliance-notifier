import os
import json
import csv
import boto3
from library.helpers.send_email import send_email


sender = os.environ.get('EMAIL_FROM_ADDRESS')
recipients = json.loads(os.environ.get('DEFAULT_EMAIL_RECIPIENTS', '[]'))

class ebs_unencrypted_volumes_analyzer:

    def __init__(self, account_id):
        self.account_id = account_id
        self.unencrypted_volumes = []

    def analyze(self, region_list):
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
                      'Name': next((tag['Value'] for tag in volume.get('Tags', []) 
                                    if tag['Key'] == 'Name'), ''),
                      'Owner': next((tag['Value'] for tag in volume.get('Tags', []) 
                                     if tag['Key'] == 'Owner'), ''),
                      'Environment': next((tag['Value'] for tag in volume.get('Tags', []) 
                                           if tag['Key'] == 'Environment'), '')
                    })
        print("EBS: Unencrypted volumes analysis complete")
        print(self.unencrypted_volumes)
        if not self.unencrypted_volumes:
            print("EBS: No unencrypted volumes found.")
            return
        print("EBS: Unencrypted volumes found, generating report...")
        self.csv()

    def csv(self):
        csv_path = f'/tmp/ebs-unencrypted-volumes-{self.account_id}.csv'
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Region', 'Availability Zone', 'Volume ID', 'Encrypted',
                          'Type', 'Attached Instances', 'IOPS', 'Size',
                          'Name', 'Owner', 'Environment']
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

          As part of our continuous compliance checks, we have identified unencrypted EBS volumes in your AWS account {self.account_id}.

          EBS volumes without encryption exposes your workloads to potential data breaches and does not align with security best practices.

          To address this:
          
            1. Review the attached report to see affected volumes by region and usage.
            2. Consider enabling encryption by default or migrating volumes to encrypted snapshots.
          

          Taking action ensures data confidentiality, strengthens your cloud security posture, and aligns with your compliance obligations.

          Regards and thanks,
          Atos Managed Services
          """,
          attachment_path=csv_path
      )
