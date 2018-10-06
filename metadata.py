#!/usr/bin/python
import boto3
import re
import dynamodb

#Initialize the session based on the aws profile we're using.  We'll only do this once
#to-do:  figure out a solution for the region so its not hard coded
def __init__(awsprofile, region):
    global ec2_client, ec2_resource
    session = boto3.session.Session(profile_name=awsprofile, region_name=region)
    ec2_client = session.client('ec2')
    ec2_resource = session.resource('ec2')

def main():
	pass

#DynDB is super picky about empty strings.  not all optional attributes are set so we must account
#for the ones that arent by setting it to None.
def enumerate_volumes(vpcid):
	tag = ''
	table_name = str('volumes-'+vpcid)
	dynamodb.dyndb_create(table_name)
	dynamodb.initialize_table(table_name)
	print("Populating EBS volume information")
	volume_metadata = ec2_resource.volumes.all()
	for i in volume_metadata:
		keytag = ''
		try:
			for key in i.tags:
				if key['Key'] == 'Name':
					keytag = key['Value']
				if keytag == '':
					keytag = 'None'
		except:
			if i.tags == None or keytag == '':
				keytag = 'None'
		mount_point = i.attachments[0]['Device']
		if i.snapshot_id == '':
			snapshot = 'None'
		else:
			snapshot = i.snapshot_id
		print("%s %s" % (i.volume_id, i.availability_zone))
		dynamodb.volume_put(table_name, i.volume_id, i.availability_zone, mount_point, snapshot, keytag)

#if __name__ == '__main__':
#    main()
