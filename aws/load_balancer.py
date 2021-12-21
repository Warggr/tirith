import boto3
from config import SECURITY_GROUP

ec2_resource = boto3.resource('ec2')
ec2 = boto3.client('ec2')
elbv2 = boto3.client('elbv2')

class LoadBalancer:
    def __init__(self):
        self.arn = None
        self.dns_name = None
    def create(self, batch_name):
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.create_load_balancer
        print('Create load balancer')
        resp = elbv2.create_load_balancer(
            Name=f'tirith-{batch_name}-load-balancer',
            Subnets = [subnet.id for subnet in ec2_resource.subnets.filter()],
            SecurityGroups=[ SECURITY_GROUP ],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        self.arn = resp['LoadBalancers'][0]['LoadBalancerArn']
        self.dns_name = resp['LoadBalancers'][0]['DNSName']
    def delete(self):
        if self.arn:
            print('Delete load balancer')
            #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/elbv2.html#ElasticLoadBalancingv2.Client.delete_load_balancer
            elbv2.delete_load_balancer(LoadBalancerArn=self.arn)
            self.arn = None
    def serialize(self):
        return {"dns_name": self.dns_name, "arn": self.arn}
    def unserialize(self, data):
        self.dns_name = data["dns_name"]
        self.arn = data["arn"]
        return self
