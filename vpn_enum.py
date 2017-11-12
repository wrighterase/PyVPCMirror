#!/usr/bin/python
import boto3
import dynamodb

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')
vpc_select = []

def vpc_info(x):
    vpc = ec2_resource.Vpc(x)
    x = (vpc.id)# + ': ' + vpc.tags[0]['Value'])
    return x

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
    
def menu_select():
    num=0
    for i in vpc_select:
        print(str(num) + ': ' + i + ': ' + ec2_resource.Vpc(i).tags[0]['Value'])
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
    
def enumerate_vpc(vpcid):
    #source_vpc = ec2_resource.Vpc(vpcid)
    #vpcid = source_vpc.id
    enumerate_rttbl(vpcid)
    enumerate_subnets(vpcid)
    enumerate_secgroups(vpcid)
    
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
        for x in i.tags:
            if x['Key'] == 'Name':
                print('%s' ' %s ' '%s') % (i.id, x['Value'], i.vpc_id)
                dynamodb.rttbl_put(table_name, i.id, x['Value'], associated_subnets, i.vpc_id)
                associated_subnets = []

def enumerate_subnets(vpcid):
    table_name = str('subnet-'+vpcid)
    dynamodb.dyndb_create(table_name)
    dynamodb.initialize_table(table_name)
    print("Populating subnet information")
    subnet_filter = ec2_resource.subnets.filter(Filters=[{'Name': 'vpc-id', 'Values': [vpcid]}])
    for i in subnet_filter:
        for x in i.tags:
            if x['Key'] == 'Name':
                print('%s' ' %s ' ' %s ' ' %s ' '%s') % (i.id, x['Value'], i.cidr_block, i.availability_zone, i.vpc_id)
                dynamodb.subnet_put(table_name, i.id, x['Value'], i.cidr_block, i.availability_zone, i.vpc_id)

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

def enumerate_ec2_instances():
    pass


if __name__ == '__main__':
    main()