import boto3
import csv
import os
from library.send_email import send_email

sender = os.environ.get('SES_SENDER')
recipient = os.environ.get('SES_RECIPIENT')

class ebs_unencrypted_volumes_analyzer:

    def __init__(self):
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
                      'Name': next((tag['Value'] for tag in volume.get('Tags', []) if tag['Key'] == 'Name'), ''),
                      'Owner': next((tag['Value'] for tag in volume.get('Tags', []) if tag['Key'] == 'Owner'), ''),
                      'Environment': next((tag['Value'] for tag in volume.get('Tags', []) if tag['Key'] == 'Environment'), '')
                    })
        self.csv()
        print("EBS: Unencrypted volumes analysis complete")
        print(self.unencrypted_volumes)        

    def csv(self):
        # Write CSV
        csv_path = '/tmp/ebs_unencrypted_volumes.csv'
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Region', 'Availability Zone', 'Volume ID', 'Encrypted',
                          'Type', 'Attached Instances', 'IOPS', 'Size', 'Name', 'Owner', 'Environment']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for volume in self.unencrypted_volumes:
                writer.writerow(volume)
        
        # self.send_email(csv_path)
        send_email(
          sender=sender,
          recipient=recipient,
          subject='Unencrypted EBS Volumes Report',
          body_text='Please see the attached file for a list of unencrypted EBS volumes.',
          attachment_path=csv_path
      )


        
