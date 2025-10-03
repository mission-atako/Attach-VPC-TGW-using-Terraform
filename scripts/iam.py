import boto3 
import csv 

def get_user_permissions(username):
    iam = boto3.client('iam')
    permissions = {
        'managed_policies': [],
        'inline_policies': [],
        'group_managed_policies': [],
        'group_inline_policies': []
    }

    try:
        response = iam.list_attached_user_policies(UserName=username)
        for policy in response['AttachedPolicies']:
            permissions['managed_policies'].append(policy['PolicyName'])

        response = iam.list_user_policies(UserName=username)
        for policy_name in response['PolicyNames']:
            permissions['inline_policies'].append(policy_name)

        response = iam.list_groups_for_user(UserName=username)
        for group in response['Groups']:
            group_name = group['GroupName']

            group_managed_policies_response = iam.list_attached_group_policies(GroupName=group_name)
            for policy in group_managed_policies_response['AttachedPolicies']:
                permissions['group_managed_policies'].append(f"{group_name}:{policy['PolicyName']}")

            group_inline_policies_response = iam.list_group_policies(GroupName=group_name)
            for policy_name in group_inline_policies_response['PolicyNames']:
                permissions['group_inline_policies'].append(f"{group_name}:{policy_name}")

    except iam.exceptions.NoSuchEntityException:
        print(f"User '{username}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return permissions

header = ['Name','User Type','Managed Policies','Inline Policies', "Group Managed Policies", "Group Inline Policies"]
with open("users.csv", 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    ## IAM USERS
    iam = boto3.client('iam')
    users = iam.list_users()
    for u in users['Users']:
        permissions = get_user_permissions(u['UserName'])
        line = [u['UserName'],'IAM User', permissions['managed_policies'],permissions['inline_policies'],permissions['group_managed_policies'],permissions['group_inline_policies']]
        writer.writerow(line)
    while True:
        if users['IsTruncated']:
            users = iam.list_users(Marker=users['Marker'])
            permissions = get_user_permissions(u['UserName'])
            line = [u['UserName'],'IAM User', permissions['managed_policies'],permissions['inline_policies'],permissions['group_managed_policies'],permissions['group_inline_policies']]
            writer.writerow(line)
        else: 
            break
    