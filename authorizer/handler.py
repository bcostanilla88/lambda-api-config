import os
import json
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

def check_if_cn_allowed(cn_value: str) -> bool:
    allowed_cnames_list = json.loads(os.environ.get("ALLOWED_CNAMES", "[]"))
    logger.debug(f"allowed_cnames={allowed_cnames_list}")
    if cn_value in allowed_cnames_list:
        return True
    return False
    

@logger.inject_lambda_context
def authorize(event, context):
    logger.debug("Authorizer start")
    token = event.get("authorizationToken")
    method_arn = event.get("methodArn")

    logger.debug(f"token={token}")
    logger.debug(f"method_arn={method_arn}")
    
    
    if not token:
        logger.warning("Missing token")
        raise Exception("Missing token")
    
    try:
        scheme, kvs = token.split(" ", 1)
        pairs = kvs.split(",")
        kv_dict = dict(pair.split("=", 1) for pair in pairs if "=" in pair)
        cn_value = kv_dict.get("CN", "")
    except ValueError:
        logger.warning(f"Error parsing token={token}")
        raise Exception("Error parsing token")
    
    effect = "Deny"
    if check_if_cn_allowed(cn_value):
        effect = "Allow"

    return generate_policy("user", effect, method_arn)