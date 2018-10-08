#!/usr/bin/python
import boto3
from datetime import datetime
from datetime import timedelta

ec2_client = session.client('ec2')

maxAMIageDays = 14
images = ec2_client.describe_images(
        Filters=[{'Name': 'tag:Name', 'Values': ['Image Created By PyVPCMirror']}],
        Owners=['self'])['Images']
    
def checkAMIforDeletion(aminame):
    print("Looking for AMI images older than %s days" % maxAMIageDays)
    for i in images:
    	createtime = datetime.strptime(i['CreationDate'], "%Y-%m-%dT%H:%M:%S.%fZ")
	    if createtime < datetime.now() - timedelta(days=maxAMIageDays):
	    	deregister_ami(i['ImageId'])
	        print("Looking for snapshots...")
	        for snapshots in i['BlockDeviceMappings']:
	            try:
	                snap_id = snapshots['Ebs']['SnapshotId']
	                delete_snap(image_id, snap_id)
	            except:
	                pass

def deregister_ami(image):
	print("\nDeregistering the following image:")
	print(i['Name'], i['ImageId'])
	ec2_client.deregister_image(ImageId=image)
	return

def delete_snap(image, snapshot):
	print("Deleting %s for %s" % (snapshot, image))
	ec2_client.delete_snapshot(SnapshotId=snapshot)
	return
