#!/bin/python3

INSTANCES_PER_CLUSTER = 1

import os
import sys
import boto3

from config import KEYPAIR_NAME, SECURITY_GROUP

IMAGE_ID = "ami-0ed9277fb7eb570c9" #Amazon Linux 2 instance

ec2_resource = boto3.resource('ec2')
ec2 = boto3.client('ec2')
elbv2 = boto3.client('elbv2')

class SubCluster:
    def __init__(self, cluster_nb):
        self.instance_type = None
        self.cluster_nb = cluster_nb
        self.instance_ids = []
        self.target_group_arn = None
        self.zone = None

    def create(self, batch_name, vpc_id, instanceType = {'type': 't2.micro', 'zone': 'us-east-1a'}):
        self.instance_type = instanceType['type']
        self.zone = instanceType['zone']
        try:
            self.create_instances(batch_name)

            self.create_target_group_if_needed(vpc_id)

            # Reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.register_targets
            targets = [ { 'Id': i, 'Port': 5000 } for i in self.instance_ids]

            elbv2.register_targets(
                    TargetGroupArn=self.target_group_arn,
                    Targets=targets
                )
        except Exception as x:
            self.delete()
            raise x

    def delete(self):
        self.delete_target_group()
        if(self.instance_ids):
            ec2.terminate_instances(InstanceIds=self.instance_ids)

    def wait_for_shutdown(self):
        print('Waiting for instances to terminate...')
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait( InstanceIds=self.instance_ids )
        self.instance_ids = []

    def htmlpath(self):
        return f'/cluster{self.cluster_nb}'

    def target_group_name(self):
        return f'cluster-{self.cluster_nb}'

    def create_instances(self, batch_name='anonymous', script_filename = os.path.expanduser('~/.tirith/become-gitserver.sh')):
        print(f'Create {INSTANCES_PER_CLUSTER} instances')

        with open(script_filename, 'r') as file:
            script = file.read()

        if os.path.exists(script):
            with open(script, 'r') as file:
                script = file.read()
        resp = ec2.run_instances(ImageId=IMAGE_ID,
                            InstanceType=self.instance_type,
                            MinCount=INSTANCES_PER_CLUSTER,
                            MaxCount=INSTANCES_PER_CLUSTER,
                            KeyName=KEYPAIR_NAME,
                            SecurityGroupIds=[SECURITY_GROUP],
                            UserData=script,
                            Placement = {
                                'AvailabilityZone': self.zone,
                            },
                            TagSpecifications=[{
                                'ResourceType': 'instance',
                                'Tags': [
                                    { 'Key': 'Name', 'Value': f'{batch_name}-{self.cluster_nb}-{self.instance_type}' },
                                    { 'Key': 'Batch', 'Value': batch_name },
                                    { 'Key': 'Cluster', 'Value': str(self.cluster_nb) }
                                ]
                            }],
                            Monitoring={
                                'Enabled': True
                            }
                        )

        self.instance_ids = [ instance['InstanceId'] for instance in resp['Instances'] ]
        for instance in resp['Instances']:
            print('INSTANCE_DNS', cluster_nb, instance['PublicDnsName'])

        waiter = ec2.get_waiter('instance_running')
        waiter.wait(InstanceIds=self.instance_ids)

    def create_target_group(self, vpc_id):
        print('Create target group')
        resp = elbv2.create_target_group(
            Name=self.target_group_name(),
            Protocol='HTTP',
            ProtocolVersion='HTTP1',
            Port=80,
            VpcId=vpc_id,
            HealthCheckEnabled=True,
            HealthCheckPath=self.htmlpath(),
            HealthCheckIntervalSeconds=10,
            HealthyThresholdCount=3,
            TargetType='instance',
            Tags=[
                {
                    'Key': 'Name',
                    'Value': f'target-group-{self.cluster_nb}'
                },
            ]
        )
        self.target_group_arn = resp['TargetGroups'][0]['TargetGroupArn']
        return self.target_group_arn

    def create_target_group_if_needed(self, vpc_id):
        try:
            self.create_target_group(vpc_id) #will succeed if the target group didn't exist, or existed with the same config
        except elbv2.exceptions.DuplicateTargetGroupNameException:
            print('Target group exists, deleting old group and create new group...')
            response = elbv2.describe_target_groups( Names=[ self.target_group_name() ] )
            elbv2.delete_target_group(TargetGroupArn=response['TargetGroups'][0]['TargetGroupArn'])

            self.create_target_group(vpc_id)

    def delete_target_group(self):
        if self.target_group_arn:
            print('Delete target group')
            #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_target_group
            elbv2.delete_target_group(TargetGroupArn=self.target_group_arn)
            self.target_group_arn = None

    def wait_for_group(self):
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Waiter.TargetInService
        waiter = elbv2.get_waiter('target_in_service')
        waiter.wait( TargetGroupArn=self.target_group_arn, WaiterConfig={ 'MaxAttempts': 60 } ) # waits 15 minutes, then throws an error

    def serialize(self):
        return { key:self.__dict__[key] 
                    for key in [ "instance_type", "instance_ids", "target_group_arn", "zone"] }
    def unserialize(self, data):
        for key in data:
            self.__dict__[key] = data[key]
        return self
