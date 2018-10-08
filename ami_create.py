import boto3
from datetime import datetime

ec2_client = boto3.client('ec2')

instances = ec2_client.describe_instances()
instances = instances['Reservations']

def lambda_handler(events, context):
    ami_creation()

def ami_creation():
    for i in instances:
        id = i['Instances'][0]['InstanceId']
        date = str(datetime.now().strftime('%m-%d-%Y'))
        try:
            for key in i['Instances'][0]['Tags']:
                if key['Key'] == 'Name':
                    keytag = key['Value']
        except:
            keytag = id
        name = ('%s %s asdfasdf' % (keytag, date))
        try:
            new_ami_id = ec2_client.create_image(Name=name,InstanceId=id,NoReboot=True)
            new_ami_id = new_ami_id['ImageId']
            create_tags(new_ami_id, id, date)
        except Exception as e:
            print(e)
            pass
        
        
def create_tags(image, id, date):
    print("Creating tags for %s" % (image))
    tag = ("PyVPCMirror Backup for %s on %s" % (id, date))
    ec2_client.create_tags(Resources=[image], Tags=[{'Key': 'Name', 'Value': tag}])