#! /usr/bin/env python
from typing import Dict, List
import boto3
from rich.console import Console

console = Console()

profile_name = ''

def get_boto_session(profile_name):
     return boto3.Session(profile_name=profile_name)


def list_profiles():
    console.print("[red]" + "Listing profiles...")
    for profile in boto3.Session().available_profiles:
        console.print("[green]" + profile)


def select_profile():
    list_profiles()
    profiles = boto3.Session().available_profiles
    profile_name = console.input("Select profile: ")
    if profile_name in profiles:
        console.print("Selected profile: " + profile_name)
        return profile_name
    else:
        console.print("Profile not found, exiting.", style="bold black on red")
        exit(1)
        
        
def get_roles():
    global profile_name
    iam = get_boto_session(profile_name).client('iam')
    roles = []
    role_paginator = iam.get_paginator('list_roles')
    for resp in role_paginator.paginate():
        for role in resp['Roles']:
            roles.append(role)
    return roles

def get_role_names():
    role_names = []
    roles = get_roles()
    for role in roles:
        role_names.append(role['RoleName'])
    return roles


def get_policies_for_roles(role_names: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """ Create a mapping of role names and any policies they have attached to them by 
        paginating over list_attached_role_policies() calls for each role name. 
        Attached policies will include policy name and ARN.
    """
    global profile_name
    iam = get_boto_session(profile_name).client('iam')
    policy_map = {}
    policy_paginator = iam.get_paginator('list_attached_role_policies')
    for name in role_names:
        role_policies = []
        for response in policy_paginator.paginate(RoleName=name):
            role_policies.extend(response.get('AttachedPolicies'))
        policy_map.update({name: role_policies})
    return policy_map


def main():
    global profile_name
    profile_name = select_profile()

    # get list of roles
    roles = get_role_names()
    for role in roles:
        console.print("[green]" + role['RoleName'])
    
    iam = get_boto_session(profile_name).client('iam')

    selected_role_string = console.input("Select role: ")
    # check if string is in roles
    if selected_role_string in [role['RoleName'] for role in roles]:
        console.print("Selected role: " + selected_role_string)
    else:
        console.print("Role not found, exiting.", style="bold black on red")
        exit(1)

    selected_role = iam.get_role(RoleName=selected_role_string)['Role']
    
    attached_policies = get_policies_for_roles([selected_role_string])


    # switch to another profile
    console.print("[red]" + "Logging in to another profile...")
    profile_name = select_profile()
    # session = boto3.Session(profile_name=profile_name)
    # session.client('iam').assume_role(RoleArn=selected_role['Arn'], RoleSessionName='my-session')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nExiting...")
        exit(1)
