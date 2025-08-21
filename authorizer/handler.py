from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()

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

@logger.inject_lambda_context
def authorize(event, context):
    effect = None
    method_arn = None
    logger.debug("Authorizer start")
    token = event.get("authorizationToken")
    logger.debug(f"token={token}")
    method_arn = event.get("methodArn")
    logger.debug(f"method_arn={method_arn}")
   
    
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