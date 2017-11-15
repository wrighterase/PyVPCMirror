#!/usr/bin/python
import boto3

def __init__(awsprofile):
    global dyndb_client, dyndb_resource, waiter
    session = boto3.session.Session(profile_name=awsprofile, region_name='us-west-2')
    dyndb_client = session.client('dynamodb')
    dyndb_resource = session.resource('dynamodb')
    waiter = dyndb_client.get_waiter('table_exists')

def dyndb_create(table_name):
    try:
        table_exists = dyndb_client.describe_table(TableName=table_name)['Table']['TableStatus']
        print("\nDatabase for " + table_name + " already exists!")
    except:
        print("\nCreating database..."),
        dyndb_client.create_table(
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'},],
                TableName=table_name,
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'},],
                ProvisionedThroughput={'ReadCapacityUnits': 5,'WriteCapacityUnits': 5})
        waiter.wait(TableName=table_name)
        print("Complete")

def initialize_table(table_name):
    global table
    table = dyndb_resource.Table(table_name)
    return table

def rttbl_put(table_name, id, tag, subnets, vpc):
    table.put_item(
            TableName=table_name,
               Item={'id': id,
                    'tag': tag,
                    'subnets': subnets,
                    'vpc': vpc})

def subnet_put(table_name, id, tag, cidr_block, az, vpc):
    table.put_item(
            TableName=table_name,
            Item={'id': id,
                    'tag': tag,
                    'cidr': cidr_block,
                    'az': az,
                    'vpc': vpc})

def secgroup_put(table_name, id, name, desc, vpc, ingress, egress):
    table.put_item(
            TableName=table_name,
            Item={'id': id,
                    'name': name,
                    'description': desc,
                    'vpc': vpc,
                    'ingress': ingress,
                    'egress': egress})
    
def instances_put(table_name, id, tag, vpc, ami, secgroups,
                  itype, az, subnet, keypair, iam, priipv4, 
                  secipv4=None, vols=None):
    table.put_item(
            TableName=table_name,
            Item={'id': id,
                    'tag': tag,
                    'vpc': vpc,
                    'ami': ami,
                    'securitygroups': secgroups,
                    'iam-profile': iam,
                    'instance-type': itype,
                    'az': az,
                    'subnet': subnet,
                    'keypair': keypair,
                    'primaryIpv4': priipv4,
                    'secondaryIpv4': secipv4,
                    'additionalEBS': vols})
                   
def table_get_item(table_name, id, item):
    item_value = table.get_item(TableName=table_name,
                                Key={'id': id})['Item'][item]
    return item_value

#if __name__ == '__main__':
#    main()