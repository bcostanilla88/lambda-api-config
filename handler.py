import json
from typing import Optional

import boto3
import os

s3 = boto3.client("s3")
bucket_name = os.environ['S3_BUCKET']
key = os.environ['S3_KEY']

class ApiConfig:
    def __init__(self, endpoint: str, method: str, target_uri: str, allowed: bool):
        self.endpoint = endpoint
        self.method = method
        self.target_uri = target_uri
        self.allowed = allowed

def load_endpoint_config(target_endpoint: str) -> Optional[ApiConfig]:
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        json_content = json.loads(content)

        matched = next((item for item in json_content if item.get("endpoint") == target_endpoint), None)

        if matched:
            return ApiConfig(**matched)
        return None
    except Exception as e:
        raise RuntimeError(f"Error loading config: {e}")

def build_response(status_code: int, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json"
        }
    }

def handle_json_request(event, target_endpoint: str):
    try:
        endpoint_obj = load_endpoint_config(target_endpoint)
        if endpoint_obj:
            if endpoint_obj.allowed:
                return build_response(200, {
                    "endpoint": endpoint_obj.endpoint,
                    "method": endpoint_obj.method,
                    "target_uri": endpoint_obj.target_uri
                })
            else:
                return build_response(403, {"error": "Access not allowed"})
        return build_response(404, {"error": "API Config not found"})
    except Exception as e:
        return build_response(500, {"error": str(e)})


def get_api_config(event, context):
    stage = event["requestContext"].get("stage")
    path = event["path"]
    return handle_json_request(event, stage + path)
