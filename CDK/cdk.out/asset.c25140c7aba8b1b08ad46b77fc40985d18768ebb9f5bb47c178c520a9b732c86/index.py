import boto3
import json

def handler(event, context):
    waf = boto3.client("wafv2")
    mode = event.get("mode", "block").lower()

    acl = waf.get_web_acl(Name="SecureWebACL", Scope="REGIONAL")
    token = acl['LockToken']
    config = acl['WebACL']

    if mode == "normal":
        rules = config.get("Rules", [])
        default_action = config.get("DefaultAction", {"Allow": {}})
    else:
        rules = []
        default_action = {"Block": {}}

    waf.update_web_acl(
        Name="SecureWebACL",
        Scope="REGIONAL",
        Id=config["Id"],
        LockToken=token,
        DefaultAction=default_action,
        VisibilityConfig=config["VisibilityConfig"],
        Rules=rules
    )

    return {
        "message": f"WAF switched to {mode} mode.",
        "applied_action": default_action
    }
