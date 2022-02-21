#! /usr/bin/env python
"""
Copies Secrets from one AWS profile to another, usually for use between AWS accounts.
"""

import boto3
from rich.console import Console

console = Console()


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


def main():
    """
    Used to copy secrets from one AWS profile to another, usually for use between AWS accounts.
    """

    profile_name = select_profile()

    # Get the Secrets Manager client
    session = boto3.Session(profile_name=profile_name)
    client = session.client("secretsmanager")

    # Get the list of secrets
    paginator = client.get_paginator("list_secrets")
    pages = paginator.paginate()
    for page in pages:
        for raw_secret in page["SecretList"]:
            # Print each secret name
            console.print("[green]" + raw_secret["Name"])

    # select secret resource to copy
    secret_name = console.input("Select secret to copy: ")

    # list secret contents by ARN
    raw_secret = client.get_secret_value(SecretId=secret_name)

    new_secret = {}

    new_secret["SecretString"] = raw_secret["SecretString"]
    new_secret["Name"] = raw_secret["Name"]

    # login to another aws profile
    console.print("[red]" + "Logging in to another profile...")
    profile_name = select_profile()

    session = boto3.Session(profile_name=profile_name)
    client = session.client("secretsmanager")

    # create new secret
    console.print("[red]" + "Creating new secret...")
    response = client.create_secret(
        Name=new_secret["Name"], SecretString=new_secret["SecretString"]
    )
    console.print(response)
    # console.print(raw_secret)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\nExiting...")
        exit(1)
