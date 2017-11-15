#!/usr/bin/python
import os
import vpc_enum
import dynamodb
#import sys

def __init__():
    profile_list = []
    awscreds = os.path.expanduser('~/.aws/credentials')
    if os.path.exists(awscreds):
        with open(awscreds, 'r') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        for profile in content:
            if profile.startswith('[') and profile.endswith(']'):
                profile_list.append(profile.strip('[]'))
        profile_select(profile_list)
    else:
        print("No credentials were found.  Execuing 'awsconfig'")
         
def profile_select(profile_list):
    print("Looking AWS credential profiles...\n")
    num=0
    for profile in profile_list:
        print(str(num) + ': ' + profile)
        num+=1
    print('\n99: Exit')
    
    while True:
        select = input('Choose an AWS profile: ')
        if select == 99:
            break
        elif select not in range(len(profile_list)):
            print("\nInvalid option")
        else:
            awsprofile = profile_list[select]
            print("\nUsing AWS profile:\n" + profile_list[select])
            main(awsprofile)
            break

def main(awsprofile):
    vpc_enum.__init__(awsprofile)
    dynamodb.__init__(awsprofile)
    vpc_enum.main()
        
if __name__ == '__main__':
    __init__()