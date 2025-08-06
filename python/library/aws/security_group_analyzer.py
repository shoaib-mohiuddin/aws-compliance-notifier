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
    
    def __init__(self, account_id, session, exclusions):
        self.account_id = account_id
        self.session = session
        self.excluded_sg_rules = exclusions.get('security_group_rule_ids', [])
        self.default_sg_rules = []
        self.errors = []
        self.sg_cache = {} # Cache for SG details
        self.excluded_rules_count = 0  # Track how many rules were excluded
    
    def analyze(self, region_list):
        """
        Identifies security groups with default 0.0.0.0/0 rule across the specified regions.
        
        Args:
            region_list (List[str]): A list of AWS regions to scan.
        """
        print("SG: Analyzing for overly permissive rules...")
        print(f"SG: Excluding {len(self.excluded_sg_rules)} security group rules from analysis")
        
        for region in region_list:
            try:
                ec2 = self.session.client('ec2', region_name=region)
                
                paginator = ec2.get_paginator('describe_security_group_rules')
                page_iterator = paginator.paginate()
                
                for page in page_iterator:
                    sg_rules = page['SecurityGroupRules']
                    
                    for rule in sg_rules:
                        self._analyze_security_group_rule(rule, region, ec2)
                        
            except ClientError as e:
                error_msg = f"Error scanning region {region}: {e}"
                print(error_msg)
                self.errors.append(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error in region {region}: {e}"
                print(error_msg)
                self.errors.append(error_msg)
        
        print(f"Analysis complete. Found {len(self.default_sg_rules)} risky rules across {len(region_list)} regions.")
        print(f"Excluded {self.excluded_rules_count} rules from the report based on exclusion list.")
        
        print(self.default_sg_rules)

        if not self.default_sg_rules:
            print("SG: No security group with unrestricted rules found.")
            return          
        return {
            "csv_data": self.default_sg_rules,
            "filename": f"security-group-analysis-{self.account_id}.csv",
            "subject": f"Security Group Analysis Report for AWS Account - {self.account_id}",
            "body_text": f"""
            Hi there,

            As part of our ongoing security compliance efforts, we have analyzed the security groups in your AWS account {self.account_id}.

            The analysis has identified security groups with overly permissive rules that allow unrestricted access. Below is a summary of the findings:

            - Total risky security group rules found: {len(self.default_sg_rules)}
            - Excluded rules from report: {self.excluded_rules_count}
            - Regions scanned: {len(region_list)}

            Please refer to the attached report for details on affected security groups and rules. We recommend reviewing these rules and applying necessary restrictions to enhance the security posture of your AWS environment. 
            If any rules are not required, consider removing them to minimize the attack surface. And if any unrestricted rules are necessary, let us know so we can update the exclusion list accordingly.

            Regards and thanks,
            Atos Managed Services
            """
        }
    
    def _analyze_security_group_rule(self, rule, region, ec2_client):
        """
        Analyze a single security group rule for risky open access.
        
        Args:
            rule (dict): Security group rule data from AWS API
            region (str): AWS region name
            ec2_client: EC2 client for additional API calls if needed
        """
        rule_id = rule.get('SecurityGroupRuleId')
        
        # Skip if rule is in exclusion list
        if rule_id in self.excluded_sg_rules:
            self.excluded_rules_count += 1
            # print(f"SG: Skipping excluded rule {rule_id}")
            return
        
        sg_id = rule.get('GroupId')
        direction = 'Ingress' if rule.get('IsEgress') == False else 'Egress'
        protocol = rule.get('IpProtocol')
        from_port = rule.get('FromPort')
        to_port = rule.get('ToPort')
        
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

        for cidr, ip_version in [(rule.get('CidrIpv4'), 'IPv4'), (rule.get('CidrIpv6'), 'IPv6')]:
            if cidr in ['0.0.0.0/0', '::/0']:
                # self._record_rule_with_open_access(rule, sg_id, region, direction, protocol_name, port_range, cidr, ip_version)
                
                ### If not using _record_rule_with_open_access as a separte method, you can directly append to the list with below 
                self.default_sg_rules.append({
                    'Account ID': self.account_id,
                    'Region': region,
                    'Security Group ID': sg_id,
                    'Direction': direction,
                    'Protocol': protocol_name,
                    'Port Range': port_range,
                    'Source/Destination CIDR': cidr,
                    'IP Version': ip_version,
                    'Rule ID': rule.get('SecurityGroupRuleId', '')
                })
    
    # def _record_rule_with_open_access(self, rule, sg_id, region, direction, protocol_name, port_range, cidr, ip_version):
    #     """
    #     Add a risky rule to the report data.
        
    #     Args:
    #         rule (dict): Security group rule data
    #         sg_id (str): Security group ID
    #         region (str): AWS region
    #         direction (str): 'Ingress' or 'Egress'
    #         protocol_name (str): Protocol name
    #         port_range (str): Port range
    #         cidr (str): CIDR block
    #         ip_version (str): 'IPv4' or 'IPv6'
    #     """
        
    #     # Get SG details from cache or API
    #     if sg_id not in self.sg_cache:
    #         try:
    #             ec2 = boto3.client('ec2', region_name=region)
    #             sg_details = ec2.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
    #             self.sg_cache[sg_id] = {
    #                 'name': sg_details.get('GroupName', ''),
    #                 'vpc_id': sg_details.get('VpcId', 'EC2-Classic')
    #             }
    #         except Exception as e:
    #             print(f"SG: Warning - Could not get security group details for {sg_id}: {e}")
    #             self.sg_cache[sg_id] = {'name': '', 'vpc_id': 'Unknown'}

    #     sg_name = self.sg_cache[sg_id]['name']
    #     vpc_id = self.sg_cache[sg_id]['vpc_id']
        
    #     self.default_sg_rules.append({
    #         'Account ID': self.account_id,
    #         'Region': region,
    #         'VPC ID': vpc_id,
    #         'Security Group ID': sg_id,
    #         'Security Group Name': sg_name,
    #         'Direction': direction,
    #         'Protocol': protocol_name,
    #         'Port Range': port_range,
    #         'Source/Destination CIDR': cidr,
    #         'IP Version': ip_version,
    #         'Description': rule.get('Description', ''),
    #         'Rule ID': rule.get('SecurityGroupRuleId', '')
    #     })
