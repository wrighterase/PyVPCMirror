#!/usr/bin/python
import boto3

#Initialize the session based on the aws profile we're using.  We'll only do this once
#to-do:  figure out a solution for the region so its not hard coded
def __init__(awsprofile, region):
    global dyndb_client, dyndb_resource, waiter
    session = boto3.session.Session(profile_name=awsprofile, region_name=region)
    dyndb_client = session.client('dynamodb')
    dyndb_resource = session.resource('dynamodb')
    waiter = dyndb_client.get_waiter('table_exists')

#Look for an existing table.  If none exists go ahead and create it/
#Wait until its completed so we're not too aggressive
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

#Set the table to work with based on what part of the mirror process we're in.
#This is required to increase runtime speed and reduce the number of calls to aws.
#This part was also needed to interact with the database with less syntax since using DynDB
#as a client requires to set the type of data being entered vs workign with it 
#as a resource.  This is cleaner.
def initialize_table(table_name):
    global table
    table = dyndb_resource.Table(table_name)
    return table

#Database put methods.  Self explanatory.
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

def volume_put(table_name, id, az, dev, snap, tag):
    table.put_item(
        TableName=table_name,
        Item={'id': id,
                'az': az,
                'dev': dev,
                'snap': snap,
                'tag': tag})

#Method to get an item from a dyntb table.  Not needed yet, but will be once we start using the data we've collected
def table_get_item(table_name, id, item):
    item_value = table.get_item(TableName=table_name,
                                Key={'id': id})['Item'][item]
    return item_value

#if __name__ == '__main__':
#    main()