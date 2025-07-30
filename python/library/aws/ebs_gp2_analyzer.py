"""
EBS GP2 Analyzer

This module checks for EBS volumes that are gp2 type. It generates 
a CSV report and sends it via SES to designated recipients.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class EbsGP2Analyzer:
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
                        'Account ID': self.account_id,
                        'Region': region,
                        'Availability Zone': availability_zone,
                        'Volume ID': volume_id,
                        'Type': volume_type,
                        'Attached Instances': vol_attachments,
                        'IOPS': iops,
                        'Size': volume_size,
                    })
        print("EBS: GP2 volumes analysis complete")
        print(self.gp2_volumes)

        if not self.gp2_volumes:
            print("EBS: No GP2 volumes found.")
            return
        return {
            "subject": f'GP2 Volumes Detected in AWS Account - {self.account_id}',
            "body_text": f"""
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
            "csv_data": self.gp2_volumes,
            "filename": f"ebs-gp2-volumes-{self.account_id}.csv"
        }
        




