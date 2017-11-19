#!/usr/bin/python
import boto3
import re
import dynamodb

vpc_select = []

#Initialize the session based on the aws profile we're using.  We'll only do this once
#to-do:  figure out a solution for the region so its not hard coded
def __init__(awsprofile):
    global ec2_client, ec2_resource
    session = boto3.session.Session(profile_name=awsprofile, region_name='us-west-2')
    ec2_client = session.client('ec2')
    ec2_resource = session.resource('ec2')

#Grabs the vpc ID based on its tag name
def vpc_info(x):
    vpc = ec2_resource.Vpc(x)
    x = (vpc.id)
    return x

#Grab all VPCs in the account that are available and resolve its VPC ID
def main():
    list_of_vpcs = ec2_client.describe_vpcs(Filters=[
        {
            'Name': 'state',
            'Values': [
                'available',
            ]
        }
    ])
    
    for i in list_of_vpcs['Vpcs']:
        vpc_select.append(vpc_info(i['VpcId']))
    menu_select()

#Dynamically create a menu selection based on the data we've collected so far
def menu_select():
    print("Gather existing a list of VPCs\n")
    num=0
    for i in vpc_select:
        try:
            vpc_tag = ec2_resource.Vpc(i).tags[0]['Value']
        except:
            vpc_tag = 'Tag not available'
        print(str(num) + ': ' + i + ': ' + vpc_tag)
        num+=1
    print('\n99: Exit')
    
    while True:
        select = input('Choose a VPC: ')
        if select == 99:
            break
        elif select not in range(len(vpc_select)):
            print("\nInvalid option")
        else:
            print("\nEnumerating on VPC:\n" + vpc_select[select])
            enumerate_vpc(vpc_select[select])
            break

#Start data collection for mirroring process in this order...
def enumerate_vpc(vpcid):
    enumerate_rttbl(vpcid)
    enumerate_subnets(vpcid)
    enumerate_secgroups(vpcid)
    enumerate_ec2_instances(vpcid)
    
def enumerate_rttbl(vpcid):
    associated_subnets = []
    table_name = str('rttbl-'+vpcid)
    dynamodb.dyndb_create(table_name)
    dynamodb.initialize_table(table_name)
    print("Populating route table information")
    rttbl_filter = ec2_resource.route_tables.filter(Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}])
    for i in rttbl_filter:
        rttbl_id = ec2_resource.RouteTable(i.id)
        for associated in rttbl_id.associations: associated_subnets.append(associated.subnet_id)
        for tag in i.tags:
            if tag['Key'] == 'Name':
                keytag = tag['Value']
                if keytag == '':
                    keytag = 'Null'
                print('%s' ' %s ' '%s') % (i.id, keytag, i.vpc_id)
                dynamodb.rttbl_put(table_name, i.id, keytag, associated_subnets, i.vpc_id)
                associated_subnets = []

def enumerate_subnets(vpcid):
    table_name = str('subnet-'+vpcid)
    dynamodb.dyndb_create(table_name)
    dynamodb.initialize_table(table_name)
    print("Populating subnet information")
    subnet_filter = ec2_resource.subnets.filter(Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}])
    for i in subnet_filter:
        for tag in i.tags:
            if tag['Key'] == 'Name':
                keytag = tag['Value']
        print('%s' ' %s ' ' %s ' ' %s ' '%s') % (i.id, keytag, i.cidr_block, i.availability_zone, i.vpc_id)
        dynamodb.subnet_put(table_name, i.id, keytag, i.cidr_block, i.availability_zone, i.vpc_id)

def enumerate_secgroups(vpcid):
    table_name = str('secgroups-'+vpcid)
    dynamodb.dyndb_create(table_name)
    dynamodb.initialize_table(table_name)
    print("Populating security group information")
    secgroups = ec2_resource.security_groups.filter(
                Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}])
    for i in secgroups:
        print('%s\t' ' %s') % (i.id, i.group_name)
        dynamodb.secgroup_put(table_name, i.id, i.group_name, i.description, 
                              i.vpc_id, i.ip_permissions, i.ip_permissions_egress)

def enumerate_ec2_instances(vpcid):
    associated_volumes = []
    secondary_ipv4 = []
    table_name = str('instances-'+vpcid)
    dynamodb.dyndb_create(table_name)
    dynamodb.initialize_table(table_name)
    print("Populating EC2 instance information")
    instances = ec2_resource.instances.filter(
                Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}])
    for i in instances:
        try:
            iam_arn = i.iam_instance_profile['Arn']
            iam_arn = re.sub('arn.*profile/', '', iam_arn)
        except:
            iam_arn = 'None'
        try:
            keypair = i.key_name
        except:
            keypair = 'None'
        volumes = i.volumes.all()
        eni = i.network_interfaces
        for v in volumes:
            associated_volumes.append(v.id)
        for tag in i.tags:
            if tag['Key'] == 'Name':
                keytag = tag['Value']
                if keytag == '':
                    keytag = 'Null'
        for n in eni:
            for ip in n.private_ip_addresses:
                if ip['Primary'] == False:
                    secondary_ipv4.append(ip['PrivateIpAddress'])
                if ip['Primary'] == True:
                    primary_ipv4 = ip['PrivateIpAddress']
        print('%s' ' %s ' ' %s ' '%s') % (i.id, keytag, keypair, i.vpc_id)
        dynamodb.instances_put(table_name, i.id, keytag, i.vpc_id, i.image_id, i.security_groups,
                               i.instance_type, i.placement['AvailabilityZone'], i.subnet_id,
                               keypair, iam_arn, primary_ipv4, secondary_ipv4, associated_volumes)
        associated_volumes = []
        secondary_ipv4 = []

        
#if __name__ == '__main__':
#    main()