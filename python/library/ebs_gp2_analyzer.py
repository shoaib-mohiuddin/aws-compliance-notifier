import boto3
import os
import csv
from library.send_email import send_email

sender = os.environ.get('SES_SENDER')
recipient = os.environ.get('SES_RECIPIENT')

class ebs_gp2_analyzer:

    def __init__(self):
        self.gp2_volumes = []

    def analyze(self, region_list):
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
                if volume_type == 'gp2':
                    if volume_state == 'in-use':
                        vol_attachments = volume['Attachments'][0]['InstanceId']
                    iops = volume['Iops']
                    self.gp2_volumes.append({
                        'Region': region,
                        'Availability Zone': availability_zone,
                        'Volume ID': volume_id,
                        'Type': volume_type,
                        'Attached Instances': vol_attachments,
                        'IOPS': iops,
                        'Size': volume_size,
                        'Name': next((tag['Value'] for tag in volume.get('Tags', []) if tag['Key'] == 'Name'), ''),
                        'Owner': next((tag['Value'] for tag in volume.get('Tags', []) if tag['Key'] == 'Owner'), ''),
                        'Environment': next((tag['Value'] for tag in volume.get('Tags', []) if tag['Key'] == 'Environment'), '')
                    })
        self.csv()
        print("EBS: GP2 volumes analysis complete")
        print(self.gp2_volumes)

    def csv(self):
        # Write CSV
        csv_path = '/tmp/ebs_gp2_volumes.csv'
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Region', 'Availability Zone', 'Volume ID', 'Type',
                          'Size', 'IOPS', 'Attached Instances', 'Name', 'Owner', 'Environment']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for volume in self.gp2_volumes:
                writer.writerow(volume)

        send_email(
          sender=sender,
          recipient=recipient,
          subject='EBS GP2 Volumes Report',
          body_text='Attached is the report of EBS volumes using gp2 type.',
          attachment_path=csv_path
        )
