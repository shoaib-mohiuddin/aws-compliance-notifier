import boto3
import csv
import os
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


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
                iops = ''
                if volume_state == 'in-use':
                    vol_attachments = volume['Attachments'][0]['InstanceId']
                if encrypted is False:
                    self.unencrypted_volumes.append({
                        'Region': region,
                        'Volume ID': volume_id,
                        'Encrypted': encrypted,
                        'Type': volume_type,
                        'Attached Instances': vol_attachments,
                        'IOPS': iops,
                        'Size': volume_size
                    })
        self.csv()
        print("EBS: Unencrypted volumes analysis complete")
        print(self.unencrypted_volumes)        

    def csv(self):
        # Write CSV
        csv_path = '/tmp/unencrypted_volumes.csv'
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['Region', 'Volume ID', 'Encrypted',
                          'Type', 'Attached Instances', 'IOPS', 'Size']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for volume in self.unencrypted_volumes:
                writer.writerow(volume)
        
        self.send_email(csv_path)
    
    def send_email(self, attachment_path='/tmp/unencrypted_volumes.csv'):
        ses = boto3.client('ses')
        sender = 'shoaibmm7@gmail.com'
        recipient = 'shoaibmm7@gmail.com'
        subject = 'Unencrypted EBS Volumes Report'
        body_text = 'Please see the attached file for a list of unencrypted EBS volumes.'

        # Create the root message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        # Attach the body
        body = MIMEText(body_text, 'plain')
        msg.attach(body)

        # Attach the CSV file
        with open(attachment_path, 'rb') as file:
            part = MIMEApplication(file.read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
            msg.attach(part)

        # Send email
        response = ses.send_raw_email(
            Source=sender,
            Destinations=[recipient],
            RawMessage={'Data': msg.as_string()}
        )

        print("Email sent! Message ID:", response['MessageId'])

        
