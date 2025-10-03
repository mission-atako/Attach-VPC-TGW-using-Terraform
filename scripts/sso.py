import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError


def get_sso_instance():
    """Get the SSO instance ARN and Identity Store ID."""
    try:
        sso_admin = boto3.client('sso-admin')
        response = sso_admin.list_instances()
        
        if not response['Instances']:
            print("No SSO instances found.")
            return None, None, None
        
        instance = response['Instances'][0]  # Usually only one instance
        instance_arn = instance['InstanceArn']
        identity_store_id = instance['IdentityStoreId']
        
        print(f"SSO Instance ARN: {instance_arn}")
        print(f"Identity Store ID: {identity_store_id}")
        print("-" * 80)
        
        return sso_admin, instance_arn, identity_store_id
    
    except ClientError as e:
        print(f"Error getting SSO instance: {e}")
        return None, None, None


def list_permission_sets(sso_admin, instance_arn):
    """List all permission sets."""
    print("\n=== PERMISSION SETS ===")
    try:
        paginator = sso_admin.get_paginator('list_permission_sets')
        permission_sets = {}
        
        for page in paginator.paginate(InstanceArn=instance_arn):
            for ps_arn in page['PermissionSets']:
                # Get permission set details
                ps_details = sso_admin.describe_permission_set(
                    InstanceArn=instance_arn,
                    PermissionSetArn=ps_arn
                )
                
                ps_info = ps_details['PermissionSet']
                permission_sets[ps_arn] = {
                    'Name': ps_info['Name'],
                    'Description': ps_info.get('Description', 'No description'),
                    'SessionDuration': ps_info.get('SessionDuration', 'Not set'),
                    'RelayState': ps_info.get('RelayState', 'Not set')
                }
                
                print(f"Name: {ps_info['Name']}")
                print(f"  ARN: {ps_arn}")
                print(f"  Description: {ps_info.get('Description', 'No description')}")
                print(f"  Session Duration: {ps_info.get('SessionDuration', 'Not set')}")
                
                # List managed policies attached to this permission set
                try:
                    policies_response = sso_admin.list_managed_policies_in_permission_set(
                        InstanceArn=instance_arn,
                        PermissionSetArn=ps_arn
                    )
                    if policies_response['AttachedManagedPolicies']:
                        print("  Managed Policies:")
                        for policy in policies_response['AttachedManagedPolicies']:
                            print(f"    - {policy['Name']} ({policy['Arn']})")
                except ClientError:
                    pass
                
                # Check for inline policy
                try:
                    inline_policy = sso_admin.get_inline_policy_for_permission_set(
                        InstanceArn=instance_arn,
                        PermissionSetArn=ps_arn
                    )
                    if inline_policy.get('InlinePolicy'):
                        print("  Inline Policy: Present")
                except ClientError:
                    pass
                
                print()
        
        return permission_sets
    
    except ClientError as e:
        print(f"Error listing permission sets: {e}")
        return {}


def get_users_and_groups(identity_store_id):
    """Get all users and groups from the identity store."""
    identitystore = boto3.client('identitystore')
    users = {}
    groups = {}
    
    print("\n=== USERS ===")
    try:
        paginator = identitystore.get_paginator('list_users')
        for page in paginator.paginate(IdentityStoreId=identity_store_id):
            for user in page['Users']:
                user_id = user['UserId']
                users[user_id] = {
                    'UserName': user.get('UserName', 'N/A'),
                    'DisplayName': user.get('DisplayName', 'N/A'),
                    'Name': user.get('Name', {}),
                    'Emails': user.get('Emails', [])
                }
                
                name = user.get('Name', {})
                full_name = f"{name.get('GivenName', '')} {name.get('FamilyName', '')}".strip()
                
                print(f"User: {user.get('UserName', 'N/A')} ({full_name})")
                print(f"  ID: {user_id}")
                if user.get('Emails'):
                    print(f"  Email: {user['Emails'][0].get('Value', 'N/A')}")
                print()
    
    except ClientError as e:
        print(f"Error listing users: {e}")
    
    print("\n=== GROUPS ===")
    try:
        paginator = identitystore.get_paginator('list_groups')
        for page in paginator.paginate(IdentityStoreId=identity_store_id):
            for group in page['Groups']:
                group_id = group['GroupId']
                groups[group_id] = {
                    'DisplayName': group.get('DisplayName', 'N/A'),
                    'Description': group.get('Description', 'No description')
                }
                
                print(f"Group: {group.get('DisplayName', 'N/A')}")
                print(f"  ID: {group_id}")
                print(f"  Description: {group.get('Description', 'No description')}")
                print()
    
    except ClientError as e:
        print(f"Error listing groups: {e}")
    
    return users, groups


def list_account_assignments(sso_admin, instance_arn, users, groups):
    """List all account assignments for users and groups."""
    print("\n=== ACCOUNT ASSIGNMENTS ===")
    
    try:
        # First, get all accounts that have assignments
        org_client = boto3.client('organizations')
        try:
            # List all accounts in the organization
            response = org_client.list_accounts()
            accounts = response['Accounts']
            account_map = {acc['Id']: acc['Name'] for acc in accounts}
        except ClientError:
            # If we can't access organizations, we'll discover accounts through assignments
            account_map = {}
            print("Note: Unable to access Organizations service. Account names may not be available.")
    
        # Get all permission sets first
        permission_sets_response = sso_admin.list_permission_sets(InstanceArn=instance_arn)
        
        assignments_found = False
        
        for ps_arn in permission_sets_response['PermissionSets']:
            # Get permission set name
            ps_details = sso_admin.describe_permission_set(
                InstanceArn=instance_arn,
                PermissionSetArn=ps_arn
            )
            ps_name = ps_details['PermissionSet']['Name']
            
            # List accounts assigned to this permission set
            try:
                accounts_paginator = sso_admin.get_paginator('list_accounts_for_provisioned_permission_set')
                
                for accounts_page in accounts_paginator.paginate(
                    InstanceArn=instance_arn,
                    PermissionSetArn=ps_arn
                ):
                    for account_id in accounts_page['AccountIds']:
                        if account_id not in account_map:
                            account_map[account_id] = f"Account-{account_id}"
                        
                        print(f"\nPermission Set: {ps_name}")
                        print(f"Account: {account_map[account_id]} ({account_id})")
                        
                        # List assignments for this permission set and account
                        assignments_paginator = sso_admin.get_paginator('list_account_assignments')
                        
                        for assignments_page in assignments_paginator.paginate(
                            InstanceArn=instance_arn,
                            AccountId=account_id,
                            PermissionSetArn=ps_arn
                        ):
                            for assignment in assignments_page['AccountAssignments']:
                                assignments_found = True
                                principal_type = assignment['PrincipalType']
                                principal_id = assignment['PrincipalId']
                                
                                if principal_type == 'USER':
                                    if principal_id in users:
                                        user_info = users[principal_id]
                                        name = user_info.get('UserName', principal_id)
                                        display_name = user_info.get('DisplayName', '')
                                        if display_name and display_name != name:
                                            name = f"{name} ({display_name})"
                                    else:
                                        name = f"Unknown User ({principal_id})"
                                    
                                    print(f"  👤 User: {name}")
                                
                                elif principal_type == 'GROUP':
                                    if principal_id in groups:
                                        group_info = groups[principal_id]
                                        name = group_info.get('DisplayName', principal_id)
                                    else:
                                        name = f"Unknown Group ({principal_id})"
                                    
                                    print(f"  👥 Group: {name}")
            
            except ClientError as e:
                if "AccessDenied" not in str(e):
                    print(f"Error listing assignments for permission set {ps_name}: {e}")
        
        if not assignments_found:
            print("No account assignments found.")
    
    except ClientError as e:
        print(f"Error listing account assignments: {e}")


def export_to_json(permission_sets, users, groups, instance_arn, identity_store_id):
    """Export all data to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"identity_center_audit_{timestamp}.json"
    
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "sso_instance_arn": instance_arn,
        "identity_store_id": identity_store_id,
        "permission_sets": permission_sets,
        "users": users,
        "groups": groups
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        print(f"\nData exported to: {filename}")
    except Exception as e:
        print(f"Error exporting to JSON: {e}")


def main():
    """Main function to run the Identity Center audit."""
    print("AWS Identity Center Audit Script")
    print("=" * 50)
    
    try:
        # Get SSO instance information
        sso_admin, instance_arn, identity_store_id = get_sso_instance()
        if not sso_admin:
            return
        
        # List permission sets
        permission_sets = list_permission_sets(sso_admin, instance_arn)
        
        # Get users and groups
        users, groups = get_users_and_groups(identity_store_id)
        
        # List account assignments
        list_account_assignments(sso_admin, instance_arn, users, groups)
        
        # Export to JSON
        export_to_json(permission_sets, users, groups, instance_arn, identity_store_id)
        
        print(f"\nSummary:")
        print(f"- Permission Sets: {len(permission_sets)}")
        print(f"- Users: {len(users)}")
        print(f"- Groups: {len(groups)}")
    
    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your AWS credentials.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()