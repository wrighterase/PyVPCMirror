#!/usr/bin/python
import os
import vpc_enum
import dynamodb
import metadata
import subprocess
import re
import itertools
#import sys

banner = """
   ___              ___  ___       _                     
  / _ \_   _/\   /\/ _ \/ __\/\/\ (_)_ __ _ __ ___  _ __ 
 / /_)/ | | \ \ / / /_)/ /  /    \| | '__| '__/ _ \| '__|
/ ___/| |_| |\ V / ___/ /__/ /\/\ \ | |  | | | (_) | |   
\/     \__, | \_/\/   \____|/    \/_|_|  |_|  \___/|_|   
       |___/                                             
"""

#Look for existing aws crednetials and populate environment profiles to choose from
#If no credentials found execute 'aws config' for the user to get them configured
def __init__():
    print(banner)
    profile_list = []
    awscreds = os.path.expanduser('~/.aws/credentials')
    if os.path.exists(awscreds):
        with open(awscreds, 'r') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        for profile in content:
            if profile.startswith('[') and profile.endswith(']'):
                profile_list.append(profile.strip('[]'))
        f.close()
        profile_select(profile_list)
    else:
        print("No credentials were found.  Executing 'awsconfig'")
        print("Please provide your AWS profile credentials\n")
        AWSCONFIG = "aws configure"
        subprocess.call(AWSCONFIG, shell=True)

#List environment profiles to verify we're working with the correct account         
def profile_select(profile_list):
    print("Looking AWS credential profiles...\n")
    num=0
    for profile in profile_list:
        print(str(num) + ': ' + profile)
        num+=1
    print('\n99: Exit')
    
    while True:
        select = int(input('Choose an AWS profile: '))
        try:
            if select == 99:
                break
            elif select not in range(len(profile_list)):
                print("\nInvalid option")
                break
            else:
                awsprofile = profile_list[select]
                print("\nUsing AWS profile: " + profile_list[select])
                #main(awsprofile)
                region_select(awsprofile)
                break
        except Exception as e:
            print(e)
            quit()

#After a named profile has been selected we need to extract the region to ensure we have a good session
#if using a profile other than default and a region has not been set this method will throw errors
def region_select(awsprofile):
    print("Looking for region associated with %s" % (awsprofile))
    region_list = []
    awsconfig = os.path.expanduser('~/.aws/config')
    try:
        if os.path.exists(awsconfig):
            with open(awsconfig, 'r') as f:
                content = f.readlines()
                content = [x.strip() for x in content]
            for region in content:
                region = re.sub('region\ =\ ', '',region) #remove 'region = ' from list
                region_list.append(region.strip('[]'))
            region = dict(itertools.izip_longest(*[iter(region_list)] * 2, fillvalue="")) #convert the list to a dictionary - izip for python2 / zip for python3
            selected_region = region[awsprofile]
    except Exception as e:
        print("Profile " + str(e) + " was not found!")
        print("Please verify that a region other than default has been set in " + awsconfig)
        print("PyVPCMirror assumes that named profiles have the required region associated")
        quit()

    print("Configured region: %s" % (selected_region))
    main(awsprofile,selected_region)

#Initialize dependent scripts and start the mirroring process
def main(awsprofile, region):
    vpc_enum.__init__(awsprofile, region)
    dynamodb.__init__(awsprofile, region)
    metadata.__init__(awsprofile, region)
    vpc_enum.main()
    #metadata_enum.main()
        
if __name__ == '__main__':
    __init__()
