import json
import boto3

waf = boto3.client("wafv2")

def handler(event, context):
    print("Received event:", json.dumps(event))

    acl_name = "SecureWebACL"
    scope = "REGIONAL"

    try:
        # Step 1: Look up WebACL by name
        acls = waf.list_web_acls(Scope=scope)['WebACLs']
        acl = next((a for a in acls if a['Name'] == acl_name), None)

        if not acl:
            raise Exception(f"WebACL '{acl_name}' not found.")

        # Step 2: Get current WebACL configuration
        acl_response = waf.get_web_acl(
            Name=acl['Name'],
            Id=acl['Id'],
            Scope=scope
        )
        web_acl = acl_response['WebACL']
        lock_token = acl_response['LockToken']

        # Step 3: Find and toggle "BlockAll" rule
        updated = False
        for rule in web_acl['Rules']:
            if rule['Name'] == 'BlockAll':
                current_action = rule['Action']
                if 'Block' in current_action:
                    rule['Action'] = {'Count': {}}
                    toggled_to = 'Count'
                else:
                    rule['Action'] = {'Block': {}}
                    toggled_to = 'Block'
                updated = True
                break

        if not updated:
            raise Exception("Rule 'BlockAll' not found in WebACL.")

        # Step 4: Update WebACL with toggled rule
        waf.update_web_acl(
            Name=web_acl['Name'],
            Id=web_acl['Id'],
            Scope=scope,
            DefaultAction=web_acl['DefaultAction'],
            Description=web_acl.get('Description') or 'Updated by Lambda',
            Rules=web_acl['Rules'],
            VisibilityConfig=web_acl['VisibilityConfig'],
            LockToken=lock_token
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"'BlockAll' rule toggled to {toggled_to}",
                "aclId": web_acl['Id']
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
