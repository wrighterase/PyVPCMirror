#!/usr/bin/python
import boto3
#import sys

dyndb_client = boto3.client('dynamodb')
dyndb_resource = boto3.resource('dynamodb')
waiter = dyndb_client.get_waiter('table_exists')

"""
dyndb_tables = []

def menu_select():
    num=0
    for i in dyndb_tables:
        print(str(num) + ': ' + i)
        num+=1
    print('\n99: Exit')
    
    while True:
        select = input('Choose an table: ')
        if select == 99:
            break
        elif select not in range(len(dyndb_tables)):
            print("\nInvalid option")
        else:
            print("\nUsing DynDB:\n" + dyndb_tables[select])
            break
            #enumerate_vpc(vpc_select[select])
        
def main():
    print("Looking for existing DynamoDB tables:")
    tables = dyndb_client.list_tables()
    for i in tables['TableNames']: dyndb_tables.append(i)
    menu_select()
"""

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
    table = dyndb_resource.Table(table_name)
    
def rttbl_put(table_name, id, tag, subnets, vpc):
    table = dyndb_resource.Table(table_name)
    table.put_item(
            TableName=table_name,
               Item={'id': id,
                    'tag': tag,
                    'subnets': subnets,
                    'vpc': vpc})
    
    """dyndb_client.put_item(
            TableName=table_name,
               Item={'id': {'S': id},
                    'tag': {'S': tag},
                    'subnets': {'L': [{'S': subnets},]},
                    'vpc': {'S': vpc}
                    })
    """
def subnet_put(table_name, id, tag, cidr_block, az, vpc):
    table = dyndb_resource.Table(table_name)
    table.put_item(
            TableName=table_name,
            Item={'id': id,
                    'tag': tag,
                    'cidr': cidr_block,
                    'az': az,
                    'vpc': vpc
                    })
            
    """
    dyndb_client.put_item(
            TableName=table_name,
               Item={'id': {'S': id},
                    'tag': {'S': tag},
                    'cidr': {'S': cidr_block},
                    'az': {'S': az},
                    'vpc': {'S': vpc}
                    })
    """
def table_get_item(table_name, id, item):
    item_value = dyndb_client.get_item(TableName=table_name,
                  Key={'id': { 'S': id}})['Item'][item]['S']
    return item_value

if __name__ == '__main__':
    main()