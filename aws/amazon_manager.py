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
        self.batch_name = 'NotConfigured'
        self.running = False
        self.deployement_percentage = 0

    def create(self, instances_per_cluster):
        self.batch_name = create_random_name()
        print('Starting batch ' + self.batch_name)
        vpc_id = next(iter(ec2_resource.vpcs.all())).id

        threads = []
        for cluster_nb, instance_type in enumerate(AmazonManager.INSTANCE_TYPE_LIST):
            child = SubCluster(cluster_nb+1)
            x = threading.Thread( target=child.create, args=(instances_per_cluster, self.batch_name, vpc_id, instance_type) )
            x.start()
            threads.append(x)
            self.children.append( child )

        self.load_balancer.create(self.batch_name)

        for thread in threads:
            thread.join()

        self.create_listener()

        print('Waiting for health checks (might take 5-10 minutes)...')
        for child in self.children:
            child.wait_for_group()
        print('Everything set up!')
        self.running = True

    def delete(self):
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
        listener = elbv2.create_listener(LoadBalancerArn=self.load_balancer.arn, Protocol='HTTP', Port=80, DefaultActions=self.stochastic())
        self.listener_arn = listener['Listeners'][0]['ListenerArn']

    def update_listener(self):
        elbv2.modify_listener(ListenerArn=self.listener_arn, DefaultActions=self.stochastic())

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
        self.update_listener()

    def more(self):
        self.deployement_percentage += 10
        if self.deployement_percentage > 100:
            self.deployement_percentage = 100
        self.update_listener()

    def delete_listener(self):
        if self.listener_arn:
            print('Delete listener')
            #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_listener
            elbv2.delete_listener(ListenerArn=self.listener_arn)
            self.listener_arn = None

    def serialize(self):
        ret = {
                key:self.__dict__[key]
                    for key in [ "batch_name", "listener_arn", "running", "deployement_percentage"] 
            }
        ret["load_balancer"] = self.load_balancer.serialize()
        ret["children"] = [ child.serialize() for child in self.children ]
        return ret
    def unserialize(self, data):
        for key in data:
            self.__dict__[key] = data[key]
        self.load_balancer = LoadBalancer().unserialize(self.load_balancer)
        self.children = [ SubCluster(i).unserialize(child) for (i,child) in enumerate(self.children) ]
        return self
