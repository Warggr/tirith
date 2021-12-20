#!/bin/python3

import random
import boto3
import threading
import sys
from load_balancer import LoadBalancer
from cluster import SubCluster
from config import SECURITY_GROUP

ec2_resource = boto3.resource('ec2')
ec2 = boto3.client('ec2')
elbv2 = boto3.client('elbv2')
rds = boto3.client('rds')
rds_data = boto3.client('rds-data')

vocals = 'aeiou'
consonants = 'bcdfghjklmnpqrstvwxz'
def create_random_name():
    ans = ''
    for i in range(3):
        ans += consonants[random.randint(0,len(consonants)-1)] + vocals[random.randint(0, len(vocals)-1)]
    return ans

class AmazonManager:
    INSTANCE_TYPE_LIST = [
        {'type': 't2.micro', 'zone': 'us-east-1a'},
        {'type': 't2.micro', 'zone': 'us-east-1b'},
    ]

    def __init__(self):
        self.children = []
        self.load_balancer = LoadBalancer()
        self.listener_arn = None
        self.database_id = 
        self.rules_arn = []
        self.batch_name = 'NotConfigured'
        self.running = False
        self.deployement_percentage = 0

    def create(self):
        self.batch_name = create_random_name()
        print('Starting batch ' + self.batch_name)
        vpc_id = next(iter(ec2_resource.vpcs.all())).id

        """response = rds.create_db_cluster(
            DBClusterIdentifier=f'{self.batch_name}-tirith-feedback',
            Engine='aurora',
            EngineMode='serverless',
            Port=3306,
            MasterUsername='kingofgondor',
            MasterUserPassword='kingofgondor',
            Tags=[
                { 'Key': 'Batch', 'Value': self.batch_name},
            ],
            ScalingConfiguration={
                'MinCapacity': 1,
                'MaxCapacity': 1,
                'AutoPause': True,
                'SecondsUntilAutoPause': 300,
                'TimeoutAction': 'RollbackCapacityChange',
                'SecondsBeforeTimeout': 60
            }
        )
        self.database_id = response['DBCluster']['DBClusterIdentifier']
        rds.authorize_db_security_group_ingress(
            DBSecurityGroupName=response['DBCluster']['VpcSecurityGroups'][0]['VpcSecurityGroupId'],
            EC2SecurityGroupId=SECURITY_GROUP
        )
        rds_data.execute_statement(database=f'{self.batch_name}-tirith-feedback')"""

        threads = []
        for cluster_nb, instance_type in enumerate(AmazonManager.INSTANCE_TYPE_LIST):
            child = SubCluster(cluster_nb+1)
            x = threading.Thread( target=child.create, args=(self.batch_name, vpc_id, instance_type) )
            x.start()
            threads.append(x)
            self.children.append( child )

        self.load_balancer.create()

        for thread in threads:
            thread.join()
        print('Waiting for health checks (might take 5-10 minutes)...')
        for child in self.children:
            child.wait_for_group()
        print('Everything set up!')
        self.running = True

    def delete(self):
        """rds.delete_db_cluster(DBClusterIdentifier=self.database_id, SkipFinalSnapshot=True)"""
        self.delete_listener()
        self.load_balancer.delete()

        for child in self.children:
            child.delete()
        for child in self.children:
            child.wait_for_shutdown()

    def stop(self):
        for child in self.children:
            child.stop()
        self.running = False

    def restart(self):
        for child in self.children:
            child.restart()
        self.running = True

    def stochastic(self):
        return [ {   
            'Type': 'forward',
            'ForwardConfig': {
                'TargetGroups': [
                    {
                        'TargetGroupArn': self.children[0].target_group_arn,
                        'Weight': 100 - self.deployement_percentage,
                    },
                    {
                        'TargetGroupArn': self.children[1].target_group_arn,
                        'Weight': self.deployement_percentage
                    }
                ],
                'TargetGroupStickinessConfig': {
                    'Enabled': True,
                    'DurationSeconds': 1200
                }
            }
        } ]

    def create_listener(self):
        print('Create listener')
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_listener
        listener = elbv2.create_listener(LoadBalancerArn=self.load_balancer.arn, Protocol='HTTP', Port=80, DefaultActions=self.stochastic(0))
        self.listener_arn = listener['Listeners'][0]['ListenerArn']

    def update_listener(self):
        elbv2.modify_listener(LoadBalancerArn=self.load_balancer.arn, DefaultActions=self.stochastic())

    def fill(self):
        self.deployement_percentage = 100
        self.update_listener()

    def switch(self):
        x = self.children.pop()
        self.children.append(x)
        self.deployement_percentage = 0
        self.update_listener()

    def less(self):
        self.deployement_percentage -= 10
        if self.deployement_percentage < 0:
            self.deployement_percentage = 0

    def more(self):
        self.deployement_percentage += 10
        if self.deployement_percentage > 100:
            self.deployement_percentage = 100

    def delete_listener(self):
        if self.listener_arn:
            print('Delete listener')
            #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_listener
            elbv2.delete_listener(ListenerArn=self.listener_arn)
            self.listener_arn = None

    def serialize(self):
        ret = {
                key:self.__dict__[key]
                    for key in [ "batch_name", "rules_arn", "listener_arn", "running"] 
            }
        ret["load_balancer"] = self.load_balancer.serialize()
        ret["children"] = [ child.serialize() for child in self.children ]
        return ret
    def unserialize(self, data):
        for key in data:
            self.__dict__[key] = data[key]
        self.load_balancer = LoadBalancer().unserialize(self.load_balancer)
        self.children = [ SubCluster(self, i).unserialize(child) for (i,child) in enumerate(self.children) ]
        return self
