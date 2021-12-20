#!/bin/python3

import sys
import boto3, botocore

ec2 = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

SECURITY_GROUP_NAME = 'white-guard-v2'

class SecurityGroup:
    def __init__(self):
        self.id = None
    def create(self):
        try:
            sec_groups = ec2.describe_security_groups(GroupNames=[ SECURITY_GROUP_NAME ])
            self.id = sec_groups['SecurityGroups'][0]['GroupId']
        except botocore.exceptions.ClientError:
            vpc = next(iter(ec2_resource.vpcs.all()))
            response = vpc.create_security_group(
                Description='Allow ssh and http',
                GroupName=SECURITY_GROUP_NAME,
            )
            self.id = response.group_id
            #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.authorize_security_group_ingress
            ec2.authorize_security_group_ingress(
                GroupId=self.id,
                IpPermissions=[
                    {
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpProtocol': 'tcp',
                        'IpRanges': [{'CidrIp': '0.0.0.0/0' }],
                        'Ipv6Ranges': [{ 'CidrIpv6': '::0/0' }],
                    },
                    {
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpProtocol': 'tcp',
                        'IpRanges': [{'CidrIp': '0.0.0.0/0' }],
                        'Ipv6Ranges': [{ 'CidrIpv6': '::0/0' }],
                    },
                ]
            )

    def delete(self):
        if self.id:
            print('Delete security group')
            try:
                #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.delete_security_group
                ec2.delete_security_group(GroupId=self.id)
                self.id = None
            except Exception as x:
                print(x)

    def serialize(self):
        return self.id
    def unserialize(self, Id):
        self.id = Id
        return self

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'create':
        sec = SecurityGroup()
        sec.create()
        print(sec.serialize())
    elif len(sys.argv) == 2 and sys.argv[1] == 'delete':
        sec = SecurityGroup().unserialize(input("Name?"))
        sec.delete()
    else:
        raise TypeError(f"Usage: {sys.argv[0]} [create|delete]")
