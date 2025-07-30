"""
Security Group Analyzer

This module checks for security groups in AWS accounts and regions that have overly permissive rules.
It generates a CSV report and sends it via SES to designated recipients.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class SecurityGroupAnalyzer:
    """
    Analyzes security groups in AWS accounts and regions for presence of default 0.0.0.0/0 rule for all ports and protocols.
    Collects data and sends a CSV report via SES.
    """
    
    def __init__(self, account_id):
        self.account_id = account_id
        self.default_sg_rules = []
        self.errors = []
    
    def analyze(self, region_list):
        """
        Identifies security groups with default 0.0.0.0/0 rule across the specified regions.
        
        Args:
            region_list (List[str]): A list of AWS regions to scan.
        """
        print("SG: Analyzing for overly permissive rules...")
        
        for region in region_list:
            try:
                ec2 = boto3.client('ec2', region_name=region)
                
                # Use pagination to handle large numbers of security groups
                paginator = ec2.get_paginator('describe_security_groups')
                page_iterator = paginator.paginate()
                
                for page in page_iterator:
                    security_groups = page['SecurityGroups']
                    
                    for sg in security_groups:
                        self._analyze_security_group(sg, region)
                        
            except ClientError as e:
                error_msg = f"Error scanning region {region}: {e}"
                print(error_msg)
                self.errors.append(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error in region {region}: {e}"
                print(error_msg)
                self.errors.append(error_msg)
        
        print(f"Analysis complete. Found {len(self.default_sg_rules)} risky rules across {len(region_list)} regions.")
        
        if not self.default_sg_rules:
            print("No security group with unrestricted rules found.")
            return
        return {
            "csv_data": self.default_sg_rules,
            "filename": f"security-group-analysis-{self.account_id}.csv",
            "subject": f"Security Group Analysis Report for AWS Account - {self.account_id}",
            "body_text": "Please find attached the security group analysis report."
        }
    
    def _analyze_security_group(self, sg, region):
        """
        Analyze a single security group for risky rules.
        
        Args:
            sg (dict): Security group data from AWS API
            region (str): AWS region name
        """
        sg_id = sg['GroupId']
        sg_name = sg.get('GroupName', '')
        vpc_id = sg.get('VpcId', 'EC2-Classic')
        
        # Check ingress rules
        ingress_rules = sg.get('IpPermissions', [])
        for rule in ingress_rules:
            self._check_rule_for_open_access(rule, sg_id, sg_name, vpc_id, region, 'Ingress')
        
        # Check egress rules (optional - usually less concerning but worth noting)
        egress_rules = sg.get('IpPermissionsEgress', [])
        for rule in egress_rules:
            self._check_rule_for_open_access(rule, sg_id, sg_name, vpc_id, region, 'Egress')
    
    def _check_rule_for_open_access(self, rule, sg_id, sg_name, vpc_id, region, direction):
        """
        Check if a rule has open access (0.0.0.0/0).
        
        Args:
            rule (dict): Security group rule
            sg_id (str): Security group ID
            sg_name (str): Security group name
            vpc_id (str): VPC ID
            region (str): AWS region
            direction (str): 'Ingress' or 'Egress'
        """
        protocol = rule.get('IpProtocol', 'N/A')
        from_port = rule.get('FromPort', 'All')
        to_port = rule.get('ToPort', 'All')
        
        # Handle protocol-specific port ranges
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
        
        if 'IpRanges' in rule:
            for ip_range in rule['IpRanges']:
                cidr = ip_range.get('CidrIp', '')
                if cidr == '0.0.0.0/0':
                    self.default_sg_rules.append({
                        'Account ID': self.account_id,
                        'Region': region,
                        'VPC ID': vpc_id,
                        'Security Group ID': sg_id,
                        'Security Group Name': sg_name,
                        'Direction': direction,
                        'Protocol': protocol_name,
                        'Port Range': port_range,
                        'Source/Destination CIDR': cidr,
                        'IP Version': 'IPv4',
                        'Description': ip_range.get('Description', '')
                    })
        
        if 'Ipv6Ranges' in rule:
            for ipv6_range in rule['Ipv6Ranges']:
                cidr = ipv6_range.get('CidrIpv6', '')
                if cidr == '::/0':
                    self.default_sg_rules.append({
                        'Account ID': self.account_id,
                        'Region': region,
                        'VPC ID': vpc_id,
                        'Security Group ID': sg_id,
                        'Security Group Name': sg_name,
                        'Direction': direction,
                        'Protocol': protocol_name,
                        'Port Range': port_range,
                        'Source/Destination CIDR': cidr,
                        'IP Version': 'IPv6',
                        'Description': ipv6_range.get('Description', '')
                    })
