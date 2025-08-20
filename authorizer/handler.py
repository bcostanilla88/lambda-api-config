def generate_policy(principal_id, effect, resource):
    if effect not in ["Allow", "Deny"]:
        raise ValueError("Effect must be Allow or Deny")
    
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource
                }
            ]
        }
    }

def authorize(event, context):
    token = event.get("authorizationToken")
    method_arn = event.get("methodArn")

    if not token:
        raise Exception("Unauthorized")
    
    try:
        scheme, kv = token.split(" ", 1)
        key, value = kv.split("=")
    except ValueError:
        raise Exception("Unauthorized")
    
    if value == "x":
        effect = "Deny"
    else:
        effect = "Allow"

    return generate_policy("user", effect, method_arn)